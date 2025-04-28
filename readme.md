# The User Management System Final Project:🎉✨🔥

### Docker image on docker hub: [Docker Link](https://hub.docker.com/r/srikar2020/user_management/tags)

![image](https://github.com/user-attachments/assets/64cdaae0-2887-45cd-865f-09a7c67c0a57)



### Issue 1: Docker compose start fail

Docker failed to start using docker compose up --build.
This was resolved by updating the Dockerfile to allow specific downgrades and completing the initial setup successfully.

[See the issue](https://github.com/srikargoud2002/user_management/commit/7eb810407cb99fbf738d163e421f8171dd3aba50)

### Issue 2: Nickname Generation Issue

Previously, a nickname was always generated even if the user provided one manually during registration.
Now, a nickname is generated only when the user does not provide it.

[See the Issue](https://github.com/srikargoud2002/user_management/issues/2)

### Issue 3: Password is not meeting the standard

Strengthened password security by enforcing stricter rules:

Minimum 8 characters

- At least one uppercase letter

- At least one lowercase letter

- At least one digit

- At least one special character


[See the issue](https://github.com/srikargoud2002/user_management/issues/6)

### Issue 4: Updation Error:

When ADMIN tries to Update the email or nickname it is causing the code to break when they are already existing. So added additional Validation Checks for both email and nickname.

[See the issue](https://github.com/srikargoud2002/user_management/issues/8)

### Issue 5: Validation Token Not being Sent to email for manual verification  

After registration, only a link was sent to verify email, without exposing the actual verification token.
Added logic to include the verification token for manual verification as well.

[See the issue](https://github.com/srikargoud2002/user_management/issues/11)

![image](https://github.com/user-attachments/assets/f3fcc7fc-132b-41ea-94e4-321b1825ecb2)


### Issue 6: Unverified Users Login Issue

When unverified users attempted to log in, the code is breaking with wrong error and not giving why to the user.
Added a clear error response instructing users to verify their account before logging in.

[See the issue](https://github.com/srikargoud2002/user_management/issues/13)


## 🚀 Feature Implemented: Advanced User Search and Filtering (Admin/Manager Access)

A powerful **search and filter** feature was implemented for **admin** and **manager** roles to easily manage users in the system.  
This functionality supports **dynamic filtering, pagination, and sorting** based on user attributes.

### ✨ Key Capabilities:

- **Pagination**:  
  Supports `skip` and `limit` parameters to efficiently paginate large sets of users.
  
- **Filtering Options**:
  - **Email**: Partial matches using `email contains`.
  - **Nickname**: Partial matches using `nickname contains`.
  - **Role**: Filter by specific role (`ADMIN`, `MANAGER`, `AUTHENTICATED`, `ANONYMOUS`).
  - **Account Status**: Filter users based on whether their account is **locked**.
  - **Professional Status**: Filter users based on their **professional** profile flag.
  - **Registration Date Range**:  
    - Filter users **registered after** (`registered_from`) a certain date.
    - Filter users **registered before** (`registered_to`) a certain date.

- **Sorting**:
  - Sort users by fields like `email`, `nickname`, `created_at`, `updated_at`, `first_name`, and `last_name`.
  - Choose sort **order** (`asc` for ascending, `desc` for descending).
  - Defaults to sorting by `created_at` in descending order if no valid field is provided.

- **Secure Role-Based Access Control**:
  - Only users with `ADMIN` or `MANAGER` roles are allowed to use this API endpoint.

- **Robust Error Handling**:
  - Invalid sort fields gracefully fall back to default.
  - Query failures are safely logged without crashing the application.

![image](https://github.com/user-attachments/assets/21c928cf-69b7-4c65-aa56-88c91b7b6909)
![image](https://github.com/user-attachments/assets/d8d33694-5f83-4b14-b31a-2334e45cddae)





### Test cases implemented

test_create_user_success, test_create_user_duplicate_email, test_get_user_success, test_get_user_not_found, test_update_user_success, test_update_user_not_found, test_delete_user_success, test_delete_user_not_found, test_list_users_success, test_register_user_success, test_register_user_conflict, test_login_success, test_login_failure, test_verify_email_success, test_verify_email_failure_invalid_token, test_login_failure_locked_account, test_login_unverified_user, test_setup_logging, test_login_user_incorrect_email, test_login_user_incorrect_password, test_account_lock_after_failed_logins, test_user_repr, test_create_user_assigns_correct_role, test_execute_query_failure, test_fetch_user_returns_none, test_update_non_existent_user, test_reset_password_non_existent_user, test_verify_email_invalid_token, test_unlock_user_account_non_existent, test_validate_email_address_valid, test_validate_email_address_invalid

Added more than **30+** Test Cases taking the test coverage to near 87%. [Link to the Commit :](https://github.com/srikargoud2002/user_management/commit/2a5f4ab8bb5240bf3ce764bdbcf23109bc2f7c48)


![image](https://github.com/user-attachments/assets/d8d32ad7-f816-41f4-a866-5c7782b40483)


### Reflection about this Course

Throughout this course on Python programming and web development, I have seen significant growth in both technical skills and professional development.

Learning Python laid a strong foundation for working with data from handling CSV files and querying SQL databases to interacting with RESTful web services. Working with FastAPI was a key milestone, showing me how to efficiently build high-performance web applications and deepening my understanding of backend development.

Version control with Git became an essential part of my workflow, teaching me best practices for collaboration and code management. Emphasis on code readability and industry standards helped me appreciate the importance of writing clean, maintainable software.

The course strengthened my grasp of object-oriented programming (OOP), helping me build modular, reusable code. Exposure to Agile methodologies further taught me how to work iteratively and adapt to changing requirements. Learning SQL and ORM patterns added another valuable skill set, enabling me to bridge application logic with efficient database design.

One of the biggest takeaways was improving my problem-solving skills  learning to debug effectively, research independently, and persist through technical challenges.

Overall, this course provided a strong, practical education in Python and web development, integrating tools like VS Code, Pytest, and REST APIs. Most importantly, it built a resilient, solution-focused mindset that will be critical in my future career in data programming and backend development.

### Link to Reflection Document:
[Reflection Document](https://drive.google.com/file/d/1u5Jt3QpyKNOnSScGOYWjV83HSjR2WlBY/view?usp=sharing)



