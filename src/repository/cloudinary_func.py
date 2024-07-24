from fastapi import HTTPException
from cloudinary.utils import cloudinary_url
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.entity.models import Photo, TransformedImage
from src.schemas.cloudinary_func import Transformation
from uuid import UUID


class CloudinaryRepository:

	@staticmethod
	async def transform_image(
			photo_id: UUID,
			transformations: List[Transformation],
			db: AsyncSession) -> str:

		try:
			# зображення з бази по ID фото (Коментарі українською потім треба видалити)
			result = await db.execute(select(Photo).filter(Photo.id == photo_id))
			photo = result.scalars().first()
			if not photo:
				raise HTTPException(status_code=404, detail="Photo not found")
			# параметри трансформації
			transform_params = {}
			for transformation in transformations:
				transform_params.update(transformation.model_dump(exclude_none=True))
			# трансформація та отримання юрл трансформації
			transform_url, _ = cloudinary_url(photo.cloudinary_id, **transform_params)
			transformed_image = TransformedImage(
				photo_id=photo.id,
				transformed_url=transform_url,

			)
			db.add(transformed_image)
			await db.commit()

			return transform_url
		except Exception as e:
			await db.rollback()
			raise HTTPException(status_code=500, detail=f"Error transforming image: {str(e)}")
