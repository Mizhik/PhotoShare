from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.user import UserSchema, UserDetail, UserLogin
from src.services.auth import auth_service
from src.repository.user import UserRepository, user_repository
from src.schemas.auth import TokenSchema

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserDetail)
async def signup(body: UserSchema, db: AsyncSession = Depends(get_db)):
    body.password = auth_service.get_password_hash(body.password)
    if await user_repository.is_user_table_empty(db):
        new_user = await user_repository.create_user(body, db, role="admin")
    else:
        new_user = await user_repository.create_user(body, db)
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    return await user_repository.login(body,db)


@router.get("/me", response_model=UserDetail)
async def user_me(current_user: UserDetail = Depends(UserRepository.get_current_user)):
    return current_user
