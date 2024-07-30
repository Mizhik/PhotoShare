from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from uuid import UUID
from src.entity.models import Rating, Photo
from src.schemas.rating import RatingResponse


class RatingRepository:

    @staticmethod
    async def create_rating(
			db: AsyncSession,
			user_id: UUID,
			photo_id: UUID,
			rating_value: int
	) -> Rating:
        """
        Creates a new rating for a given photo.

        Args:
            db (AsyncSession): The database session object for asynchronous database operations.
            user_id (UUID): The ID of the user creating the rating.
            photo_id (UUID): The ID of the photo being rated.
            rating_value (int): The rating value (must be between 1 and 5).

        Returns:
            Rating: The created rating object.

        Raises:
            HTTPException: If the rating value is not between 1 and 5 (400), if the user has already rated the photo (400), 
                           if the photo is not found (404), if the user attempts to rate their own photo (400), 
                           or if an error occurs during the creation (500).
        """

        if rating_value < 1 or rating_value > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5.")

        existing_rating = await RatingRepository.get_user_rating_for_photo(db, user_id, photo_id)
        if existing_rating:
            raise HTTPException(status_code=400, detail="User has already rated this photo.")

        photo = await db.execute(select(Photo).where(Photo.id == photo_id))
        photo = photo.scalars().first()
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found.")
        if photo.user_id == user_id:
            raise HTTPException(status_code=400, detail="Cannot rate your own photo.")
        try:
            rating = Rating(user_id=user_id, photo_id=photo_id, rating=rating_value)
            db.add(rating)
            await db.commit()
            await db.refresh(rating)
            return rating
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Error creating rating.")

    @staticmethod
    async def get_user_rating_for_photo(
        db: AsyncSession, rating_id: UUID) -> Rating | None:
        """
        Retrieves a user's rating for a specific photo.

        Args:
            db (AsyncSession): The database session object for asynchronous database operations.
            user_id (UUID): The ID of the user.
            photo_id (UUID): The ID of the photo.

        Returns:
            Rating | None: The rating object if found, otherwise None.
        """
        result = await db.execute(
            select(Rating).where(Rating.id == rating_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_average_rating(db: AsyncSession, photo_id: UUID) -> float:
        """
        Retrieves the average rating for a specific photo.

        Args:
            db (AsyncSession): The database session object for asynchronous database operations.
            photo_id (UUID): The ID of the photo.

        Returns:
            float: The average rating of the photo, or 0.0 if no ratings are found.
        """
        result = await db.execute(
			select(func.avg(Rating.rating)).where(Rating.photo_id == photo_id)
		)
        avg_rating = result.scalar()
        return avg_rating if avg_rating is not None else 0.0

    @staticmethod
    async def get_ratings_for_photo(
			db: AsyncSession,
			photo_id: UUID
	) -> list[RatingResponse]:
        """
        Retrieves all ratings for a specific photo.

        Args:
            db (AsyncSession): The database session object for asynchronous database operations.
            photo_id (UUID): The ID of the photo.

        Returns:
            list[RatingResponse]: A list of rating response objects associated with the photo.
        """
        result = await db.execute(select(Rating).where(Rating.photo_id == photo_id))
        ratings = result.scalars().all()
        return [RatingResponse.model_validate(rating) for rating in ratings]

    @staticmethod
    async def delete_rating(db: AsyncSession, rating_id: UUID) -> None:
        """
        Deletes a rating by its ID.

        Args:
            db (AsyncSession): The database session object for asynchronous database operations.
            rating_id (UUID): The ID of the rating to delete.

        Raises:
            HTTPException: If the rating is not found (404) or if an error occurs during the deletion (500).
        """
        try:
            rating = await RatingRepository.get_user_rating_for_photo(
                db, rating_id
            )
            if rating:
                await db.delete(rating)
                await db.commit()
            else:
                raise HTTPException(status_code=404, detail="Rating not found.")
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Error deleting rating.")
