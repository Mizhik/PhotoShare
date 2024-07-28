from sqlalchemy import desc, asc, func
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from typing import List, Optional
from src.entity.models import Photo, Tag, User, Rating
from src.schemas.photo import PhotoSearchQuery, SortBy, Order


class SearchPhotoRepository:
	@staticmethod
	async def search_photos(
			db: AsyncSession,
			description: Optional[str] = None,
			tag: Optional[str] = None,
			username: Optional[str] = None,
			sort_by: SortBy = SortBy.date,
			order: Order = Order.asc
	) -> List[PhotoSearchQuery]:
		try:
			query = select(Photo).options(
				selectinload(Photo.tags),
				selectinload(Photo.transformed_images)
			)

			if description:
				query = query.filter(Photo.description.ilike(f"%{description}%"))
			if tag:
				query = query.join(Photo.tags).filter(Tag.name == tag)
			if username:
				query = query.join(User).filter(User.username == username)

			sort_order = desc if order == Order.desc else asc

			if sort_by == SortBy.rating:
				avg_rating = func.coalesce(func.avg(Rating.rating), 0)
				query = query.outerjoin(Photo.ratings).group_by(Photo.id).order_by(sort_order(avg_rating))
			else:
				query = query.order_by(sort_order(Photo.created_at))

			result = await db.execute(query)
			photos = result.scalars().all()
			return photos
		except IntegrityError:
			await db.rollback()
			raise HTTPException(status_code=500, detail="Error searching for photos.")
