from builtins import Exception, bool, classmethod, int, str
from datetime import datetime, timezone
from fastapi import HTTPException
import secrets
from typing import Optional, Dict, List
from pydantic import ValidationError
from sqlalchemy import func, null, update, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_email_service, get_settings
from app.models.user_model import User
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.utils.nickname_gen import generate_nickname
from app.utils.security import generate_verification_token, hash_password, verify_password
from uuid import UUID
from app.services.email_service import EmailService
from app.models.user_model import UserRole
import logging
from datetime import date

settings = get_settings()
logger = logging.getLogger(__name__)

from sqlalchemy import and_

class UserService:

    @classmethod
    async def search_users(
        cls,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        email: Optional[str] = None,
        nickname: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_locked: Optional[bool] = None,
        is_professional: Optional[bool] = None,
        registered_from: Optional[date] = None,
        registered_to: Optional[date] = None,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> tuple[int, List[User]]:

        filters = []

        if email:
            filters.append(User.email.ilike(f"%{email}%"))
        if nickname:
            filters.append(User.nickname.ilike(f"%{nickname}%"))
        if role:
            filters.append(User.role == role)
        if is_locked is not None:
            filters.append(User.is_locked == is_locked)
        if is_professional is not None:
            filters.append(User.is_professional == is_professional)
        if registered_from:
            filters.append(User.created_at >= registered_from)
        if registered_to:
            filters.append(User.created_at <= registered_to)

        # Allowlist of sortable fields
        sort_columns = {
            "email": User.email,
            "nickname": User.nickname,
            "created_at": User.created_at,
            "updated_at": User.updated_at,
            "first_name": User.first_name,
            "last_name": User.last_name
        }

        # Fallback to created_at if sort_by is invalid
        sort_column = sort_columns.get(sort_by, User.created_at)
        sort_expr = sort_column.desc() if order.lower() == "desc" else sort_column.asc()

        try:
            query = select(User).where(and_(*filters)).order_by(sort_expr).offset(skip).limit(limit)
            total_query = select(func.count()).select_from(User).where(and_(*filters))

            result = await cls._execute_query(session, query)
            total_result = await session.execute(total_query)

            users = result.scalars().all() if result else []
            total_count = total_result.scalar()

            return total_count, users

        except Exception as e:
            logger.error(f"Search users failed: {e}")
            return 0, []

    @classmethod
    async def _execute_query(cls, session: AsyncSession, query):
        try:
            result = await session.execute(query)
            await session.commit()
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            await session.rollback()
            return None

    @classmethod
    async def _fetch_user(cls, session: AsyncSession, **filters) -> Optional[User]:
        query = select(User).filter_by(**filters)
        result = await cls._execute_query(session, query)
        return result.scalars().first() if result else None

    @classmethod
    async def get_by_id(cls, session: AsyncSession, user_id: UUID) -> Optional[User]:
        return await cls._fetch_user(session, id=user_id)

    @classmethod
    async def get_by_nickname(cls, session: AsyncSession, nickname: str) -> Optional[User]:
        return await cls._fetch_user(session, nickname=nickname)

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: str) -> Optional[User]:
        return await cls._fetch_user(session, email=email)

    @classmethod
    async def create(cls, session: AsyncSession, user_data: Dict[str, str], email_service: EmailService) -> Optional[User]:
        try:
            validated_data = UserCreate(**user_data).model_dump()

            existing_user = await cls.get_by_email(session, validated_data['email'])
            if existing_user:
                logger.error("User with given email already exists.")
                raise HTTPException(status_code=400, detail="Email already exists.")

            # Check for provided nickname
            provided_nickname = validated_data.get('nickname')
            if provided_nickname:
                if await cls.get_by_nickname(session, provided_nickname):
                    raise HTTPException(status_code=400, detail="Nickname already exists. Please try a different one.")
                nickname = provided_nickname
            else:
                nickname = generate_nickname()
                while await cls.get_by_nickname(session, nickname):
                    nickname = generate_nickname()

            validated_data['nickname'] = nickname
            validated_data['hashed_password'] = hash_password(validated_data.pop('password'))

            new_user = User(**validated_data)

            user_count = await cls.count(session)
            new_user.role = UserRole.ADMIN if user_count == 0 else UserRole.ANONYMOUS

            if new_user.role == UserRole.ADMIN:
                new_user.email_verified = True
            else:
                new_user.verification_token = generate_verification_token()

            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)  # Ensure user.id is available

            # ✅ Now it's safe to send the verification email
            if new_user.role != UserRole.ADMIN:
                await email_service.send_verification_email(new_user)

            logger.info(f"User created: {new_user.email} ({new_user.role})")
            return new_user

        except ValidationError as e:
            logger.error(f"Validation error during user creation: {e}")
            return None

        except HTTPException as ve:
            logger.warning(f"User creation failed: {ve.detail}")
            raise ve

        except Exception as e:
            logger.exception("Unexpected error during user creation")
            raise HTTPException(status_code=500, detail="An unexpected error occurred during user creation.")



    @classmethod
    async def update(cls, session: AsyncSession, user_id: UUID, update_data: Dict[str, str]) -> Optional[User]:
        try:
            # validated_data = UserUpdate(**update_data).dict(exclude_unset=True)
            validated_data = UserUpdate(**update_data).model_dump(exclude_unset=True)

            if 'password' in validated_data:
                validated_data['hashed_password'] = hash_password(validated_data.pop('password'))
            query = update(User).where(User.id == user_id).values(**validated_data).execution_options(synchronize_session="fetch")
            await cls._execute_query(session, query)
            updated_user = await cls.get_by_id(session, user_id)
            if updated_user:
                session.refresh(updated_user)  # Explicitly refresh the updated user object
                logger.info(f"User {user_id} updated successfully.")
                return updated_user
            else:
                logger.error(f"User {user_id} not found after update attempt.")
            return None
        except Exception as e:  # Broad exception handling for debugging
            logger.error(f"Error during user update: {e}")
            return None

    @classmethod
    async def delete(cls, session: AsyncSession, user_id: UUID) -> bool:
        user = await cls.get_by_id(session, user_id)
        if not user:
            logger.info(f"User with ID {user_id} not found.")
            return False
        await session.delete(user)
        await session.commit()
        return True

    @classmethod
    async def list_users(cls, session: AsyncSession, skip: int = 0, limit: int = 10) -> List[User]:
        query = select(User).offset(skip).limit(limit)
        result = await cls._execute_query(session, query)
        return result.scalars().all() if result else []

    @classmethod
    async def register_user(cls, session: AsyncSession, user_data: Dict[str, str], get_email_service) -> Optional[User]:
        return await cls.create(session, user_data, get_email_service)
    

    @classmethod
    async def login_user(cls, session: AsyncSession, email: str, password: str) -> Optional[User]:
        user = await cls.get_by_email(session, email)
        if user:
            if not user.email_verified:
                raise HTTPException(status_code=403, detail="Email not verified. Please check your inbox for a verification link.")

            if user.is_locked:
                raise HTTPException(status_code=403, detail="Your account is locked due to too many failed login attempts.")

            if verify_password(password, user.hashed_password):
                user.failed_login_attempts = 0
                user.last_login_at = datetime.now(timezone.utc)
                session.add(user)
                await session.commit()
                return user
            else:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= settings.max_login_attempts:
                    user.is_locked = True
                session.add(user)
                await session.commit()

        raise HTTPException(status_code=401, detail="Incorrect email or password.")


    @classmethod
    async def is_account_locked(cls, session: AsyncSession, email: str) -> bool:
        user = await cls.get_by_email(session, email)
        return user.is_locked if user else False


    @classmethod
    async def reset_password(cls, session: AsyncSession, user_id: UUID, new_password: str) -> bool:
        hashed_password = hash_password(new_password)
        user = await cls.get_by_id(session, user_id)
        if user:
            user.hashed_password = hashed_password
            user.failed_login_attempts = 0  # Resetting failed login attempts
            user.is_locked = False  # Unlocking the user account, if locked
            session.add(user)
            await session.commit()
            return True
        return False

    @classmethod
    async def verify_email_with_token(cls, session: AsyncSession, user_id: UUID, token: str) -> bool:
        user = await cls.get_by_id(session, user_id)
        if user and user.verification_token == token:
            user.email_verified = True
            user.verification_token = None

            # ✅ Only update role if user was previously anonymous
            if user.role == UserRole.ANONYMOUS:
                user.role = UserRole.AUTHENTICATED

            session.add(user)
            await session.commit()
            return True
        return False

    @classmethod
    async def count(cls, session: AsyncSession) -> int:
        """
        Count the number of users in the database.

        :param session: The AsyncSession instance for database access.
        :return: The count of users.
        """
        query = select(func.count()).select_from(User)
        result = await session.execute(query)
        count = result.scalar()
        return count
    
    @classmethod
    async def unlock_user_account(cls, session: AsyncSession, user_id: UUID) -> bool:
        user = await cls.get_by_id(session, user_id)
        if user and user.is_locked:
            user.is_locked = False
            user.failed_login_attempts = 0  # Optionally reset failed login attempts
            session.add(user)
            await session.commit()
            return True
        return False
