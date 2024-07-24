from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class CommentBase(BaseModel):
	text: str


class CommentCreate(CommentBase):
	pass


class CommentUpdate(CommentBase):
	pass


class CommentResponse(CommentBase):
	id: UUID
	created_at: datetime
	updated_at: datetime
	user_id: UUID
	photo_id: UUID

	class Config:
		from_attributes = True
