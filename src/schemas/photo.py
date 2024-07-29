from datetime import datetime
from typing import Optional, List
from uuid import UUID
from src.schemas.tag import TagResponse
from src.schemas.cloudinary_func import TransformedImageResponse
from src.schemas.coment import CommentResponse
from pydantic import BaseModel
from enum import Enum


class PhotoUpdate(BaseModel):
	description: Optional[str] = None


class PhotoResponse(BaseModel):
	id: UUID
	cloudinary_id: str
	url: str
	description: Optional[str] = None
	user_id: UUID
	tags: Optional[List[TagResponse]] = None
	transformed_images: Optional[List[TransformedImageResponse]] = None
	comments: Optional[List[CommentResponse]] = None
	created_at: datetime
	updated_at: datetime


class SortBy(str, Enum):
	date = 'date'
	rating = 'rating'


class Order(str, Enum):
	asc = 'asc'
	desc = 'desc'


class PhotoSearchQuery(BaseModel):
	description: Optional[str] = None
	tag: Optional[str] = None
	username: Optional[str] = None
	sort_by: SortBy = SortBy.date
	order: Order = Order.asc

	class Config:
		orm_mode = True
