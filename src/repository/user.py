from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserDetail, UserSchema
from src.services.auth import auth_service

security = HTTPBearer()


class UserRepository:

    async def is_user_table_empty(self, db: AsyncSession) -> bool:
        result = await db.execute(select(func.count()).select_from(User))
        count = result.scalar()
        return count == 0

    async def get_user_by_email(self, email: str, db: AsyncSession):
        stmt = select(User).filter_by(email=email)
        user = await db.execute(stmt)
        user = user.scalar_one_or_none()
        return user

    async def create_user(
        self, body: UserSchema, db: AsyncSession, role: str | None = None
    ) -> UserDetail:
        new_user = User(**body.model_dump())
        if role:
            new_user.role = role
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    async def login(self, body: UserSchema, db: AsyncSession):
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

    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db),
    ):
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
