from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel


class PhotoUpdate(BaseModel):
	description: Optional[str] = None
# TODO: add tags handling


class PhotoResponse(BaseModel):
	id: UUID
	cloudinary_id: str
	url: str
	description: Optional[str] = None
	user_id: UUID
	tags: Optional[List[UUID]] = None
	transformed_image: Optional[List[UUID]] = None
	comments: Optional[List[UUID]] = None
	created_at: datetime
	updated_at: datetime


class PhotoSearchQuery(BaseModel):
	description: Optional[str] = None
	tag: Optional[str] = None
	sort_by: Optional[str] = "created_at"
	descending: Optional[bool] = False
	username: Optional[str] = None

	class Config:
		from_attributes = True
