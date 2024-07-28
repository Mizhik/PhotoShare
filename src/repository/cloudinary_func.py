from fastapi import HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.entity.models import Photo, TransformedImage, User
from src.schemas.cloudinary_func import Transformation
from uuid import UUID
import cloudinary
import cloudinary.uploader
import cloudinary.api


class CloudinaryRepository:

	@staticmethod
	async def transform_image(
			photo_id: UUID,
			transformations: List[Transformation],
			description: str,
			db: AsyncSession,
			user: User
			) -> str:

		try:
			result = await db.execute(select(Photo).filter(Photo.id == photo_id))
			photo = result.scalars().first()
			if not photo:
				raise HTTPException(status_code=404, detail="Photo not found")
			transform_params = {}
			for transformation in transformations:
				transform_params.update(transformation.model_dump(exclude_none=True))
			response = cloudinary.uploader.upload(photo.url, transformation=transform_params)
			transform_url = response['url']
			transformed_image = TransformedImage(
				photo_id=photo.id,
				transformed_url=transform_url,

			)

			transformed_photo = Photo(
				url=transform_url,
				cloudinary_id=response['public_id'],
				description=description,
				user_id=user.id,
				tags=photo.tags
			)
			db.add(transformed_photo)
			db.add(transformed_image)
			await db.commit()

			return transform_url
		except Exception as e:
			await db.rollback()
			raise HTTPException(status_code=500, detail=f"Error transforming image: {str(e)}")
