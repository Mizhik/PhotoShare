from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import Role, User
from src.schemas.user import UserDetail, UserSchema
from src.services.auth import auth_service

security = HTTPBearer()


class UserRepository:

    async def is_user_table_empty(self, db: AsyncSession) -> bool:
        """
        Checks if the user table is empty.

        Args:
            db (AsyncSession): The database session object for asynchronous database operations.

        Returns:
            bool: True if the user table is empty, False otherwise.
        """
        result = await db.execute(select(func.count()).select_from(User))
        count = result.scalar()
        return count == 0

    async def get_user_by_email(self, email: str, db: AsyncSession):
        """
        Retrieves a user by their email.

        Args:
            email (str): The email of the user to retrieve.
            db (AsyncSession): The database session object for asynchronous database operations.

        Returns:
            User | None: The user object if found, otherwise None.
        """
        stmt = select(User).filter_by(email=email)
        user = await db.execute(stmt)
        user = user.scalar_one_or_none()
        return user

    async def create_user(
        self, body: UserSchema, db: AsyncSession, role: str | None = None
    ) -> UserDetail:
        """
        Creates a new user.

        Args:
            body (UserSchema): The schema containing user details.
            db (AsyncSession): The database session object for asynchronous database operations.
            role (str | None): The role to assign to the user, if any.

        Returns:
            UserDetail: The created user object.
        """
        new_user = await self.get_user_by_email(email=body.email,db=db)
        if new_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
            )
        body.password = auth_service.get_password_hash(body.password)
        new_user = User(**body.model_dump())
        if role:
            new_user.role = role
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    async def login(self, body: UserSchema, db: AsyncSession):
        """
        Authenticates a user and generates an access token.

        Args:
            body (UserSchema): The schema containing login details.
            db (AsyncSession): The database session object for asynchronous database operations.

        Returns:
            dict: A dictionary containing the access token.

        Raises:
            HTTPException: If the email or password is invalid.
        """
        user = await self.get_user_by_email(body.email, db)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
            )
        if not auth_service.verify_password(body.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
            )
        access_token = auth_service.create_access_token(data={"sub": user.email})
        return {
            "access_token": access_token,
        }

    async def change_role(self, user_id: UUID, db: AsyncSession, role:Role):
        """
        Changes the role of a user.

        Args:
            user_id (UUID): The ID of the user whose role is to be changed.
            db (AsyncSession): The database session object for asynchronous database operations.
            role (Role): The new role to assign to the user.

        Returns:
            User: The updated user object.

        Raises:
            HTTPException: If the user is not found.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await db.execute(stmt)
        user = user.scalar_one_or_none()
        if user:
            user.role = role
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db),
    ):
        """
        Retrieves the current authenticated user based on the provided credentials.

        Args:
            credentials (HTTPAuthorizationCredentials): The authorization credentials.
            db (AsyncSession): The database session object for asynchronous database operations.

        Returns:
            User: The current authenticated user.

        Raises:
            HTTPException: If the user is not found or unauthorized.
        """
        token = credentials.credentials
        email = auth_service.get_current_user_with_token(token)
        user = await db.execute(select(User).where(User.email == email))
        user = user.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        return user


user_repository = UserRepository()
