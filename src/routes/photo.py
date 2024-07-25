from datetime import datetime
from typing import Sequence
from uuid import UUID

import cloudinary
from cloudinary import uploader as cloudinary_uploader
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.configuration.settings import config
from src.database.db import get_db
from src.entity.models import User, Photo, Role
from src.repository.photo import photo_repository
from src.repository.user import UserRepository
from src.schemas.photo import PhotoUpdate, PhotoResponse
from src.services.decorators import roles_required

router = APIRouter(prefix='/photo', tags=['photos'])
cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
    secure=True
)


@router.get('/', response_model=list[PhotoResponse])
async def get_all_photos(
        offset: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_db)
) -> Sequence[Photo]:
    """
    Retrieve a paginated list of photos.

    :param offset: The number of records to skip before starting to collect the result set. Defaults to 0.
    :type offset: int
    :param limit: The number of records to return. Defaults to 10.
    :type limit: int
    :param db: The database session.
    :type db: AsyncSession
    :return: A list of photos.
    :rtype: Sequence[Photo]
    """
    return await photo_repository.get_all_photos(offset, limit, db)


@router.get('/{photo_id}', response_model=PhotoResponse)
async def get_photo_by_id(
        photo_id: UUID,
        db: AsyncSession = Depends(get_db)
) -> Photo | None:
    """
    Retrieve a photo by its ID.

    :param photo_id: The UUID of the photo to retrieve.
    :type photo_id: UUID
    :param db: The database session.
    :type db: AsyncSession
    :return: The photo if found.
    :rtype: Photo
    :raises HTTPException: If the photo is not found.
    """
    return await photo_repository.get_photo_by_id_or_404(photo_id, db)


@router.post('/upload', status_code=status.HTTP_201_CREATED, response_model=PhotoResponse)
@roles_required((Role.admin, Role.user))
async def upload_user_photo(
        description: str = Form(None),
        tags: list[str] = Form(None),
        file: UploadFile = File(),
        current_user: User = Depends(UserRepository.get_current_user),
        db: AsyncSession = Depends(get_db)
) -> Photo:
    """
    Upload a new photo for the current user.

    :param description: The description of the photo.
    :type description: str
    :param tags: A list of tags associated with the photo.
    :type tags: list[str]
    :param file: The photo file to upload.
    :type file: UploadFile
    :param current_user: The current authenticated user.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The uploaded photo.
    :rtype: Photo
    """
    public_id = f'{datetime.now().timestamp()}_{current_user.email}'
    resource = cloudinary_uploader.upload(file.file, public_id=public_id)

    return await photo_repository.save_photo_to_db(
        public_id, resource['secure_url'], description, tags, current_user, db
    )


@router.put('/{photo_id}', response_model=PhotoResponse)
@roles_required((Role.admin, Role.user))
async def update_photo(
        photo_id: UUID,
        body: PhotoUpdate,
        current_user: User = Depends(UserRepository.get_current_user),
        db: AsyncSession = Depends(get_db)
) -> Photo:
    """
    Update an existing photo's details.

    :param photo_id: The UUID of the photo to update.
    :type photo_id: UUID
    :param body: The update details for the photo.
    :type body: PhotoUpdate
    :param current_user: The current authenticated user.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The updated photo.
    :rtype: Photo
    :raises HTTPException: If the user is not authorized to update the photo.
    """
    photo = await photo_repository.get_photo_by_id_or_404(photo_id, db)

    if not current_user.is_admin and current_user.id != photo.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You cannot do it')

    uploaded_photo = await photo_repository.update_photo(photo, body, db)

    return uploaded_photo


@router.delete('/{photo_id}')
@roles_required((Role.admin, Role.user))
async def delete_photo(
        photo_id: UUID,
        current_user: User = Depends(UserRepository.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Delete a photo by its ID.

    :param photo_id: The UUID of the photo to delete.
    :type photo_id: UUID
    :param current_user: The current authenticated user.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: A message indicating the photo was deleted successfully.
    :rtype: dict
    :raises HTTPException: If the user is not authorized to delete the photo.
    """
    photo = await photo_repository.get_photo_by_id_or_404(photo_id, db)

    if not current_user.is_admin and current_user.id != photo.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You cannot do it')

    cloudinary_uploader.destroy(public_id=photo.cloudinary_id)

    await photo_repository.delete_photo(photo, db)
    return {'detail': 'Photo was deleted successfully.'}
