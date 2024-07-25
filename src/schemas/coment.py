from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class CommentBase(BaseModel):
    text: str


class CommentCreate(BaseModel):
    text:str


class CommentUpdate(BaseModel):
    text:str


class CommentResponse(BaseModel):
    id: UUID
    text:str
    created_at: datetime
    updated_at: datetime
    user_id: UUID
    photo_id: UUID

    class Config:
        from_attributes = True
