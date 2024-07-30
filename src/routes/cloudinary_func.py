from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID


from src.schemas.cloudinary_func import TransformImageRequest
from src.repository.cloudinary_func import CloudinaryRepository
from src.database.db import get_db
from src.entity.models import Role, User
from src.services.decorators import roles_required
from src.repository.user import UserRepository
from src.repository.photo import photo_repository

router = APIRouter(prefix="/transform-image", tags=["transform-image"])


@roles_required(Role.user)
@router.post("/")
async def transform_image(
		photo_id: UUID,
		request: TransformImageRequest,
		db: AsyncSession = Depends(get_db),
		current_user: User = Depends(UserRepository.get_current_user)
):
	"""
    Transforms an image with specified transformations.

    Args:
        photo_id (UUID): The ID of the photo to transform.
        request (TransformImageRequest): The request body containing transformation details and description.
        db (AsyncSession, optional): The database session object for asynchronous database operations. Defaults to Depends(get_db).
        current_user (User, optional): The current authenticated user. Defaults to Depends(UserRepository.get_current_user).

    Returns:
        dict: A dictionary containing the URL of the transformed image.

    Raises:
        HTTPException:
            - 403: If the current user is not authorized to transform the photo.
            - 404: If the photo is not found.
            - 500: If there is an internal server error.
    """
	try:
		photo = await photo_repository.get_photo_by_id_or_404(photo_id, db)

		if current_user.id != photo.user_id:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not autorized")
		transformed_url = await CloudinaryRepository.transform_image(
			photo_id=photo_id,
			transformations=request.transformations,
			description=request.description,
			db=db,
			user=current_user
		)

		return {"transformed_url": transformed_url}
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
