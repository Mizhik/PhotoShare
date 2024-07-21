from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, model_validator
from uuid import UUID

from src.entity.models import Role


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=3, max_length=50)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=8)
    role: Role


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserDetail(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: Optional[datetime] = None
    role: Role

    class Config:
        from_attributes = True
