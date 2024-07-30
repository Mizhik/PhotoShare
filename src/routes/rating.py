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


# @roles_required((Role.admin, Role.moderator, Role.user))
@router.post("/{photo_id}", response_model=RatingResponse)
async def create_rating(
    photo_id: UUID,
    rating_data: RatingCreate,
    current_user: User = Depends(UserRepository.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RatingResponse:
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
    await photo_repository.get_photo_by_id_or_404(photo_id, db)
    avg_rating = await RatingRepository.get_average_rating(db, photo_id)
    avg_rating_rounded = round(avg_rating, 2)
    return AverageRatingResponse(average_rating=avg_rating_rounded)


@roles_required((Role.admin, Role.moderator))
@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating(
    rating_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user),
) -> None:
    if not current_user.is_admin and not current_user.is_moderator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You cannot do it"
        )
    else:
        await RatingRepository.delete_rating(db, rating_id)


@roles_required((Role.admin, Role.moderator))
@router.get("/{photo_id}", response_model=List[RatingResponse])
async def get_ratings_for_photo(
    photo_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user),
) -> List[RatingResponse]:
    ratings = await RatingRepository.get_ratings_for_photo(db, photo_id)

    if not current_user.is_admin and current_user.is_moderator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You cannot do it"
        )

    return ratings
