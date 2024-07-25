from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from src.entity.models import Tag


class TagRepository:

    @staticmethod
    async def get_tag(db: AsyncSession, tag_name: str) -> Tag:
        try:
            result = await db.execute(
				select(Tag).filter(Tag.name == tag_name)
			)
            tag = result.scalars().first()
            if tag:
                return tag

        except IntegrityError:
            await db.rollback()
            raise Exception(f"Could not create or retrieve tag: {tag_name}")

    @staticmethod
    async def create_tag(db: AsyncSession, tag_name: str) -> Tag:
        try:
            new_tag = Tag(name=tag_name)
            print(type(new_tag))
            db.add(new_tag)
            await db.commit()
            await db.refresh(new_tag)
            return new_tag

        except IntegrityError:
            await db.rollback()
            raise Exception(f"Could not create or retrieve tag: {tag_name}")
