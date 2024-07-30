from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Role
from src.services.decorators import roles_required
from src.database.db import get_db
from src.schemas.user import UserChangeRole, UserSchema, UserDetail, UserLogin, UserUpdate
from src.services.auth import auth_service
from src.repository.user import UserRepository, user_repository
from src.schemas.auth import TokenSchema

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserDetail)
async def signup(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    Sign up a new user.

    **Request Body:**

    - `body` (UserSchema): A schema containing user registration details. Includes:
        - `email` (str): The user's email address.
        - `password` (str): The user's password.

    **Dependencies:**

    - `db` (AsyncSession): The database session for async operations.

    **Responses:**

    - **201 Created**: Returns the details of the newly created user. The response model is `UserDetail`.

    **Raises:**

    - `HTTPException` with status code `500 Internal Server Error` if there is an error creating the user.


    """
    body.password = auth_service.get_password_hash(body.password)
    if await user_repository.is_user_table_empty(db):
        new_user = await user_repository.create_user(body, db, role="admin")
    else:
        new_user = await user_repository.create_user(body, db)
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Log in a user and obtain an access token.

    **Request Body:**

    - `body` (UserLogin): A schema containing login credentials. Includes:
        - `email` (str): The user's email address.
        - `password` (str): The user's password.

    **Dependencies:**

    - `db` (AsyncSession): The database session for async operations.

    **Responses:**

    - **200 OK**: Returns a token schema containing the access token. The response model is `TokenSchema`.

    **Raises:**

    - `HTTPException` with status code `401 Unauthorized` if the email or password is invalid.


    """
    return await user_repository.login(body,db)


@router.get("/me", response_model=UserDetail)
async def user_me(current_user: UserDetail = Depends(UserRepository.get_current_user)):
    """
    Get details of the currently logged-in user.

    **Dependencies:**

    - `current_user` (UserDetail): The currently logged-in user, obtained from the current session.

    **Responses:**

    - **200 OK**: Returns the details of the currently logged-in user. The response model is `UserDetail`.


    """
    return current_user


@roles_required((Role.admin))
@router.put("/change-role/{user_id}", response_model=UserChangeRole)
async def change_role(
    user_id: UUID,
    role:Role,
    current_user: UserDetail = Depends(UserRepository.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change the role of a user.

    **Path Parameters:**

    - `user_id` (UUID): The ID of the user whose role is to be changed.
    - `role` (Role): The new role to assign to the user. Must be one of the defined roles.

    **Dependencies:**

    - `current_user` (UserDetail): The currently logged-in user, obtained from the current session.
    - `db` (AsyncSession): The database session for async operations.

    **Responses:**

    - **200 OK**: Returns the details of the user with the updated role. The response model is `UserChangeRole`.

    **Raises:**

    - `HTTPException` with status code `403 Forbidden` if the current user is not an admin.
    - `HTTPException` with status code `404 Not Found` if the user to update is not found.

    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You cannot do it')
    else:
        return await user_repository.change_role(user_id, db, role)
