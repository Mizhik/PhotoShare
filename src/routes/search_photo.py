from fastapi import APIRouter, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.photo import PhotoResponse, SortBy, Order
from src.repository.search_photo import SearchPhotoRepository
from src.database.db import get_db
from src.entity.models import Role, User
from src.services.decorators import roles_required
from src.repository.user import UserRepository

router = APIRouter(prefix='/search_photos', tags=['search_photos'])


@roles_required((Role.admin, Role.moderator, Role.user))
@router.get("/", response_model=List[PhotoResponse])
async def search_photos(
        description: Optional[str] = None,
        tag: Optional[str] = None,
        username: Optional[str] = None,
        sort_by: SortBy = SortBy.date,
        order: Order = Order.asc,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(UserRepository.get_current_user),
):
    """
    Search for photos based on various criteria.

    **Query Parameters:**

    - `description` (Optional[str]): A keyword to search in the photo description.
    - `tag` (Optional[str]): A tag to filter photos by.
    - `username` (Optional[str]): A username to filter photos by the owner. This parameter is optional
      and is only required if the current user has an admin or moderator role.
    - `sort_by` (SortBy): The attribute to sort the results by. Defaults to `SortBy.date`.
    - `order` (Order): The order of sorting. Defaults to `Order.asc` (ascending). Use `Order.desc` for descending.

    **Dependencies:**

    - `db` (AsyncSession): The database session for async operations.
    - `current_user` (User): The user making the request, obtained from the current session.

    **Responses:**

    - **200 OK**: Returns a list of `PhotoResponse` objects representing the photos matching the search criteria.

    **Raises:**

    - `HTTPException` with status code `403 Forbidden` if the user is not authorized to perform the search.
    

    """
    photos = await SearchPhotoRepository.search_photos(
        db=db,
        description=description,
        tag=tag,
        username=username if current_user.role in ["admin", "moderator"] else None,
        sort_by=sort_by,
        order=order
    )
    return [PhotoResponse(**photo.__dict__) for photo in photos]
