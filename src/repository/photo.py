from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.repository.tag import TagRepository
from src.entity.models import Photo, User
from src.schemas.photo import PhotoUpdate


class PhotoRepository:
    async def get_all_photos(
        self, offset: int, limit: int, db: AsyncSession
    ) -> Sequence[Photo]:
        """
        Retrieve a list of photos from the database with pagination.

        :param offset: The number of records to skip before starting to collect the result set.
        :type offset: int
        :param limit: The number of records to return.
        :type limit: int
        :param db: The database session.
        :type db: AsyncSession
        :return: A list of photos.
        :rtype: Sequence[Photo]
        """
        result = await db.execute(select(Photo).offset(offset).limit(limit))
        photos = result.scalars().all()

        return photos

    async def get_photo_by_id_or_404(
        self, photo_id: UUID, db: AsyncSession
    ) -> Photo | None:
        """
        Retrieve a photo by its ID or raise a 404 error if not found.

        :param photo_id: The UUID of the photo to retrieve.
        :type photo_id: UUID
        :param db: The database session.
        :type db: AsyncSession
        :return: The photo if found.
        :rtype: Photo
        :raises HTTPException: If the photo is not found.
        """
        result = await db.execute(select(Photo).filter_by(id=photo_id))
        photo = result.scalar_one_or_none()

        if not photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Photo was not found."
            )

        return photo

    async def save_photo_to_db(
        self,
        public_id: str,
        url: str,
        description: str,
        tags: list[str],
        user: User,
        db: AsyncSession,
    ) -> Photo:
        """
        Save a new photo to the database.

        :param public_id: The public ID of the photo in Cloudinary.
        :type public_id: str
        :param url: The URL of the photo.
        :type url: str
        :param description: The description of the photo.
        :type description: str
        :param tags: A list of tags associated with the photo.
        :type tags: list[str]
        :param user: The user who owns the photo.
        :type user: User
        :param db: The database session.
        :type db: AsyncSession
        :return: The saved photo.
        :rtype: Photo
        """
        tag_objects = []
        for tag_name in tags:
            tag = await TagRepository.create_tag(db, tag_name)
            tag_objects.append(tag)

        photo = Photo(
            url=url, cloudinary_id=public_id, description=description, user_id=user.id
        )
        db.add(photo)
        for tag in tag_objects:
            photo.tags.append(tag)

        await db.commit()
        await db.refresh(photo)

        return photo

    async def update_photo(
        self, photo: Photo, body: PhotoUpdate, db: AsyncSession
    ) -> Photo | None:
        """
        Update an existing photo's details.

        :param photo: The photo to update.
        :type photo: Photo
        :param body: The update details for the photo.
        :type body: PhotoUpdate
        :param db: The database session.
        :type db: AsyncSession
        :return: The updated photo.
        :rtype: Photo
        """
        photo.description = body.description
        db.add(photo)

        await db.commit()
        await db.refresh(photo)

        return photo

    async def delete_photo(self, photo: Photo, db: AsyncSession) -> None:
        """
        Delete a photo from the database.

        :param photo: The photo to delete.
        :type photo: Photo
        :param db: The database session.
        :type db: AsyncSession
        """
        await db.delete(photo)
        await db.commit()


photo_repository = PhotoRepository()
