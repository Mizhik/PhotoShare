from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from src.database.db import get_db
from src.repository.rating import RatingRepository
from src.schemas.rating import RatingCreate, RatingResponse, AverageRatingResponse
from src.entity.models import Role, User
from src.services.decorators import roles_required
from src.repository.user import UserRepository
from src.repository.photo import photo_repository

router = APIRouter(prefix="/rating", tags=["rating"])


@router.post("/{photo_id}", response_model=RatingResponse)
async def create_rating(
    photo_id: UUID,
    rating_data: RatingCreate,
    current_user: User = Depends(UserRepository.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RatingResponse:
    """
    Create a rating for a specific photo.

    **Path Parameters:**

    - `photo_id` (UUID): The ID of the photo to be rated.

    **Request Body:**

    - `rating_data` (RatingCreate): The rating information, including the rating value.

    **Dependencies:**

    - `current_user` (User): The user creating the rating, obtained from the current session.
    - `db` (AsyncSession): The database session for async operations.

    **Responses:**

    - **200 OK**: Returns a `RatingResponse` containing the created rating details.

    **Raises:**

    - `HTTPException` with status code `400 Bad Request` if the rating value is invalid.
    - `HTTPException` with status code `403 Forbidden` if the user is not authorized to rate.


    """
    rating = await RatingRepository.create_rating(
        db=db,
        user_id=current_user.id,
        photo_id=photo_id,
        rating_value=rating_data.rating,
    )
    return RatingResponse.model_validate(rating)


@router.get("/average-rating/{photo_id}", response_model=AverageRatingResponse)
async def get_average_rating(
    photo_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> AverageRatingResponse:
    """
    Retrieve the average rating for a specific photo.

    **Path Parameters:**

    - `photo_id` (UUID): The ID of the photo for which the average rating is to be retrieved.

    **Dependencies:**

    - `db` (AsyncSession): The database session for async operations.

    **Responses:**

    - **200 OK**: Returns an `AverageRatingResponse` containing the average rating of the photo.

    **Raises:**

    - `HTTPException` with status code `404 Not Found` if the photo with the given ID does not exist.

    """
    await photo_repository.get_photo_by_id_or_404(photo_id, db)
    avg_rating = await RatingRepository.get_average_rating(db, photo_id)
    avg_rating_rounded = round(avg_rating, 2)
    return AverageRatingResponse(average_rating=avg_rating_rounded)


@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
@roles_required((Role.admin, Role.moderator))
async def delete_rating(
    rating_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user),
) -> None:
    """
    Delete a rating by its ID.

    **Path Parameters:**

    - `rating_id` (UUID): The ID of the rating to be deleted.

    **Dependencies:**

    - `current_user` (User): The user requesting the deletion, obtained from the current session.
    - `db` (AsyncSession): The database session for async operations.

    **Responses:**

    - **204 No Content**: The rating has been successfully deleted.

    **Raises:**

    - `HTTPException` with status code `403 Forbidden` if the user is not authorized to delete the rating.
    - `HTTPException` with status code `404 Not Found` if the rating with the given ID does not exist.

    """
    await RatingRepository.delete_rating(db, rating_id)


@router.get("/{photo_id}", response_model=List[RatingResponse])
@roles_required((Role.admin, Role.moderator))
async def get_ratings_for_photo(
    photo_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user),
) -> List[RatingResponse]:
    """
    Retrieve all ratings for a specific photo.

    **Path Parameters:**

    - `photo_id` (UUID): The ID of the photo for which ratings are to be retrieved.

    **Dependencies:**

    - `current_user` (User): The user requesting the ratings, obtained from the current session.
    - `db` (AsyncSession): The database session for async operations.

    **Responses:**

    - **200 OK**: Returns a list of `RatingResponse` objects containing the details of all ratings for the photo.

    **Raises:**

    - `HTTPException` with status code `403 Forbidden` if the user is not authorized to view the ratings.


    """
    ratings = await RatingRepository.get_ratings_for_photo(db, photo_id)
    return ratings
