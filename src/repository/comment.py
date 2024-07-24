from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from uuid import UUID
from datetime import datetime, timezone
from src.entity.models import Comment
from sqlalchemy.exc import IntegrityError
from collections.abc import Sequence


class CommentRepository:

	@staticmethod
	async def create_comment(db: AsyncSession, text: str, user_id: UUID, photo_id: UUID) -> Comment:
		try:
			comment = Comment(text=text, user_id=user_id, photo_id=photo_id)
			db.add(comment)
			await db.commit()
			await db.refresh(comment)
			return comment
		except IntegrityError as e:
			await db.rollback()
			print(f"Error creating comment: {e}")
			raise HTTPException(status_code=500, detail="Error create comment")

	@staticmethod
	async def get_comment_by_id(db: AsyncSession, comment_id: UUID) -> Comment:
		result = await db.execute(select(Comment).where(Comment.id == comment_id))
		return result.scalars().first()

	@staticmethod
	async def update_comment(db: AsyncSession, comment_id: UUID, new_text: str) -> Comment:
		try:
			comment = await CommentRepository.get_comment_by_id(db, comment_id)
			if comment:
				comment.text = new_text
				comment.updated_at = datetime.now(timezone.utc)
				await db.commit()
				await db.refresh(comment)
				return comment
			else:
				raise HTTPException(status_code=404, detail="Comment not found")
		except IntegrityError as e:
			await db.rollback()
			print(f"Error updating comment: {e}")
			raise HTTPException(status_code=500, detail="Error update comment")

	@staticmethod
	async def delete_comment(db: AsyncSession, comment_id: UUID) -> None:
		try:
			comment = await CommentRepository.get_comment_by_id(db, comment_id)
			if comment:
				await db.delete(comment)
				await db.commit()
			else:
				raise HTTPException(status_code=404, detail="Comment not found")
		except IntegrityError as e:
			await db.rollback()
			print(f"Error delete comment: {e}")
			raise HTTPException(status_code=500, detail="Error delete comment")

	@staticmethod
	async def get_comment_by_photo_id(db: AsyncSession, photo_id: UUID) -> Sequence[Comment]:
		result = await db.execute(select(Comment).where(Comment.photo_id == photo_id))
		return result.scalars().all()
