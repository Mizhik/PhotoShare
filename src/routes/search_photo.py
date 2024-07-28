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
    photos = await SearchPhotoRepository.search_photos(
        db=db,
        description=description,
        tag=tag,
        username=username if current_user.role in ["admin", "moderator"] else None,
        sort_by=sort_by,
        order=order
    )
    return [PhotoResponse(**photo.__dict__) for photo in photos]
