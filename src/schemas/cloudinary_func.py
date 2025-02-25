from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class Transformation(BaseModel):
	width: Optional[int] = Field(None, description="Width")
	height: Optional[int] = Field(None, description="Height")
	crop: Optional[str] = Field(None, description="Crop type (e.g., 'fill', 'fit')")
	gravity: Optional[str] = Field(None, description="Gravity for crop (e.g., 'center', 'face')")
	radius: Optional[int] = Field(None, description="Radius for rounded corners")
	effect: Optional[str] = Field(None, description="Effect to apply (e.g., 'sepia', 'grayscale')")
	angle: Optional[int] = Field(None, description="Angle for rotation")
	border: Optional[str] = Field(None, description="Border to add")


class TransformedImageResponse(BaseModel):
	id: UUID
	transformed_url: str
	qr_code_url: Optional[str] = None

	class Config:
		from_attributes = True


class TransformImageRequest(BaseModel):
	transformations: List[Transformation]
	description: str
