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

router = APIRouter(prefix="/photo", tags=["photos"])
cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
    secure=True,
)


@router.get("/", response_model=list[PhotoResponse])
async def get_all_photos(
    offset: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
) -> Sequence[Photo]:
    """
    Retrieve a list of photos with pagination.

    **Query Parameters:**

    - `offset` (int, optional): The number of photos to skip before starting to collect the result set. Defaults to `0`.
    - `limit` (int, optional): The maximum number of photos to return. Defaults to `10`.

    **Dependencies:**

    - `db` (AsyncSession): The database session for async operations.

    **Responses:**

    - **200 OK**: Returns a list of photos. The response model is a list of `PhotoResponse`.


    """
    return await photo_repository.get_all_photos(offset, limit, db)


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo_by_id(
    photo_id: UUID, db: AsyncSession = Depends(get_db)
) -> Photo | None:
    """
    Retrieve a photo by its ID.

    **Path Parameters:**

    - `photo_id` (UUID): The ID of the photo to retrieve.

    **Dependencies:**

    - `db` (AsyncSession): The database session for async operations.

    **Responses:**

    - **200 OK**: Returns the details of the requested photo. The response model is `PhotoResponse`.
    - **404 Not Found**: If the photo with the specified ID is not found.

    """
    return await photo_repository.get_photo_by_id_or_404(photo_id, db)


@router.post(
    "/upload", status_code=status.HTTP_201_CREATED, response_model=PhotoResponse
)
@roles_required((Role.admin, Role.user))
async def upload_user_photo(
    description: str = Form(None),
    tags: list[str] = Form(None),
    file: UploadFile = File(),
    current_user: User = Depends(UserRepository.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Photo:
    """
    Upload a new photo.

    **Form Parameters:**

    - `description` (str, optional): A description for the photo.
    - `tags` (list[str], optional): A list of tags associated with the photo.
    - `file` (UploadFile, required): The file of the photo to upload.

    **Dependencies:**

    - `current_user` (User): The currently logged-in user.
    - `db` (AsyncSession): The database session for async operations.

    **Responses:**

    - **201 Created**: Returns the details of the uploaded photo. The response model is `PhotoResponse`.


    """
    return await photo_repository.save_photo_to_db(
        file, description, tags, current_user, db
    )


@router.put("/{photo_id}", response_model=PhotoResponse)
async def update_photo(
    photo_id: UUID,
    body: PhotoUpdate,
    current_user: User = Depends(UserRepository.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Photo:
    """
    Update a photo's details.

    **Path Parameters:**

    - `photo_id` (UUID): The ID of the photo to update.

    **Request Body:**

    - `body` (PhotoUpdate): A schema containing the updated photo details. Includes:
        - `description` (str, optional): Updated description of the photo.
        - `tags` (list[str], optional): Updated list of tags for the photo.

    **Dependencies:**

    - `current_user` (User): The currently logged-in user.
    - `db` (AsyncSession): The database session for async operations.

    **Responses:**

    - **200 OK**: Returns the updated photo details. The response model is `PhotoResponse`.
    - **403 Forbidden**: If the user does not have permission to update the photo.
    - **404 Not Found**: If the photo with the specified ID is not found.

    """
    photo = await photo_repository.get_photo_by_id_or_404(photo_id, db)

    if not current_user.is_admin and current_user.id != photo.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You cannot do it"
        )

    uploaded_photo = await photo_repository.update_photo(photo, body, db)

    return uploaded_photo


@router.delete("/{photo_id}")
async def delete_photo(
    photo_id: UUID,
    current_user: User = Depends(UserRepository.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a photo.

    **Path Parameters:**

    - `photo_id` (UUID): The ID of the photo to delete.

    **Dependencies:**

    - `current_user` (User): The currently logged-in user.
    - `db` (AsyncSession): The database session for async operations.

    **Responses:**

    - **204 No Content**: The photo was successfully deleted.
    - **403 Forbidden**: If the user does not have permission to delete the photo.
    - **404 Not Found**: If the photo with the specified ID is not found.

    """
    photo = await photo_repository.get_photo_by_id_or_404(photo_id, db)

    if not current_user.is_admin and current_user.id != photo.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You cannot do it"
        )

    cloudinary_uploader.destroy(public_id=photo.cloudinary_id)

    await photo_repository.delete_photo(photo, db)
    return {"detail": "Photo was deleted successfully."}
