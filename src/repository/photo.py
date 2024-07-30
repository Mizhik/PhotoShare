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
        Retrieve a paginated list of photos from the database.

        **Parameters:**

        - `offset` (int): The number of photos to skip before starting to collect the result set.
        - `limit` (int): The maximum number of photos to return.
        - `db` (AsyncSession): The database session for async operations.

        **Returns:**

        - `Sequence[Photo]`: A sequence of `Photo` objects.

        """
        result = await db.execute(select(Photo).offset(offset).limit(limit))
        photos = result.scalars().all()

        return photos

    async def get_photo_by_id_or_404(
        self, photo_id: UUID, db: AsyncSession
    ) -> Photo | None:
        """
        Retrieve a photo by its ID. Raises an HTTP 404 exception if the photo is not found.

        **Parameters:**

        - `photo_id` (UUID): The ID of the photo to retrieve.
        - `db` (AsyncSession): The database session for async operations.

        **Returns:**

        - `Photo | None`: The `Photo` object if found; otherwise, raises an HTTP 404 exception.

        **Raises:**

        - `HTTPException`: If the photo with the specified ID is not found.

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
        Save a new photo to the database with optional tags.

        **Parameters:**

        - `public_id` (str): The public ID of the photo in Cloudinary.
        - `url` (str): The URL of the photo.
        - `description` (str): A description of the photo.
        - `tags` (list[str]): A list of tags for the photo.
        - `user` (User): The user who uploaded the photo.
        - `db` (AsyncSession): The database session for async operations.

        **Returns:**

        - `Photo`: The saved `Photo` object.

        **Raises:**

        - `HTTPException`: If more than 5 tags are provided.
        """
        photo = Photo(
            url=url, cloudinary_id=public_id, description=description, user_id=user.id
        )

        if tags:
            str_tag = tags[0]
            list_tags = [result for result in str_tag.split(",")]
            tag_objects = []
            
            if len(list_tags) > 5:
                raise HTTPException(status_code=500, detail="Error. You can add only 5 tags.")

            for tag_name in list_tags:
                tag = await TagRepository.get_tag(db, tag_name)
                if not tag:
                    tag = await TagRepository.create_tag(db, tag_name)
                tag_objects.append(tag)

            for tag in tag_objects:
                photo.tags.append(tag)

        db.add(photo)
        await db.commit()
        await db.refresh(photo)
        return photo

    async def update_photo(
        self, photo: Photo, body: PhotoUpdate, db: AsyncSession
    ) -> Photo | None:
        """
        Update an existing photo's details.

        **Parameters:**

        - `photo` (Photo): The `Photo` object to update.
        - `body` (PhotoUpdate): The new details to update in the photo.
        - `db` (AsyncSession): The database session for async operations.

        **Returns:**

        - `Photo | None`: The updated `Photo` object.

        """
        photo.description = body.description
        db.add(photo)

        await db.commit()
        await db.refresh(photo)

        return photo

    async def delete_photo(self, photo: Photo, db: AsyncSession) -> None:
        """
        Delete a photo from the database.

        **Parameters:**

        - `photo` (Photo): The `Photo` object to delete.
        - `db` (AsyncSession): The database session for async operations.

        **Returns:**

        - None

        """
        await db.delete(photo)
        await db.commit()


photo_repository = PhotoRepository()
