import pytest
from httpx import AsyncClient
from uuid import uuid4
from urllib.parse import urlencode


@pytest.mark.asyncio
async def test_create_user_success(async_client, admin_token):
    payload = {
        "email": "newuser@example.com",
        "password": "Password123!",
        "nickname": "newuser",
        "role": "AUTHENTICATED"
    }
    response = await async_client.post("/users/", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@example.com"

@pytest.mark.asyncio
async def test_create_user_duplicate_email(async_client, admin_token, user):
    payload = {
        "email": user.email,
        "password": "Password123!",
        "nickname": "newnickname",
        "role": "AUTHENTICATED"
    }
    response = await async_client.post("/users/", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_get_user_success(async_client, admin_token, user):
    response = await async_client.get(f"/users/{user.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["id"] == str(user.id)

@pytest.mark.asyncio
async def test_get_user_not_found(async_client, admin_token):
    response = await async_client.get(f"/users/{uuid4()}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_user_success(async_client, admin_token, user):
    payload = {"nickname": "updatednickname"}
    response = await async_client.put(f"/users/{user.id}", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["nickname"] == "updatednickname"

@pytest.mark.asyncio
async def test_update_user_not_found(async_client, admin_token):
    payload = {"nickname": "something"}
    response = await async_client.put(f"/users/{uuid4()}", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_user_success(async_client, admin_token, user):
    response = await async_client.delete(f"/users/{user.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_delete_user_not_found(async_client, admin_token):
    response = await async_client.delete(f"/users/{uuid4()}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_list_users_success(async_client, admin_token):
    response = await async_client.get("/users/", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert "items" in response.json()

@pytest.mark.asyncio
async def test_register_user_success(async_client):
    payload = {
        "email": "registeruser@example.com",
        "password": "RegisterPass123!",
        "nickname": "registeruser",
        "role": "AUTHENTICATED"
    }
    response = await async_client.post("/register/", json=payload)
    assert response.status_code == 200
    assert response.json()["email"] == "registeruser@example.com"

@pytest.mark.asyncio
async def test_register_user_conflict(async_client, user):
    payload = {
        "email": user.email,
        "password": "AnyPass123!",
        "nickname": "conflictuser",
        "role": "AUTHENTICATED"
    }
    response = await async_client.post("/register/", json=payload)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_login_success(async_client, verified_user):
    payload = {
        "username": verified_user.email,
        "password": "MySuperPassword$1234"
    }
    response = await async_client.post("/login/", data=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_failure(async_client):
    payload = {
        "username": "wronguser@example.com",
        "password": "wrongpassword"
    }
    response = await async_client.post("/login/", data=payload)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_verify_email_success(async_client, user, db_session):
    # Fake setting token manually
    token = "validtoken123"
    user.verification_token = token
    await db_session.commit()
    await db_session.refresh(user)

    response = await async_client.get(f"/verify-email/{user.id}/{token}")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_login_failure_locked_account(async_client, locked_user, db_session):
    payload = {
        "username": locked_user.email,
        "password": "AnyPassword123!"
    }
    response = await async_client.post(
        "/login/",
        data=urlencode(payload),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Account locked due to too many failed login attempts."

@pytest.mark.asyncio
async def test_verify_email_failure_invalid_token(async_client, user, db_session):
    invalid_token = "wrongtoken"
    user.verification_token = "correcttoken"
    await db_session.commit()
    await db_session.refresh(user)

    response = await async_client.get(f"/verify-email/{user.id}/{invalid_token}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired verification token"