from pydantic import BaseModel, Field
from uuid import UUID


class RatingCreate(BaseModel):
	rating: int = Field(..., description="Rating value between 1 and 5")


class AverageRatingResponse(BaseModel):
	average_rating: float


class RatingResponse(BaseModel):
	user_id: UUID
	photo_id: UUID
	rating: int

	class Config:
		from_attributes = True
