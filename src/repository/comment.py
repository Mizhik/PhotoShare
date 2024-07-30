from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from uuid import UUID
from src.entity.models import Comment, Photo
from sqlalchemy.exc import IntegrityError
from collections.abc import Sequence


class CommentRepository:

    @staticmethod
    async def create_comment(
        db: AsyncSession, text: str, user_id: UUID, photo_id: UUID
    ) -> Comment:
        """
        Creates a new comment for a given photo.

        Args:
            db (AsyncSession): The database session object for asynchronous database operations.
            text (str): The text of the comment.
            user_id (UUID): The ID of the user creating the comment.
            photo_id (UUID): The ID of the photo being commented on.

        Returns:
            Comment: The created comment object.

        Raises:
            HTTPException: If the photo is not found (404) or if an error occurs during the creation (500).
        """
        result = await db.execute(select(Photo).where(Photo.id == photo_id))  #
        photo = result.scalars().first()
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found")  #
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
        """
        Retrieves a comment by its ID.

        Args:
            db (AsyncSession): The database session object for asynchronous database operations.
            comment_id (UUID): The ID of the comment to retrieve.

        Returns:
            Comment: The comment object if found, otherwise None.
        """
        result = await db.execute(select(Comment).where(Comment.id == comment_id))
        return result.scalars().first()

    @staticmethod
    async def update_comment(
        db: AsyncSession, comment_id: UUID, new_text: str
    ) -> Comment:
        """
        Updates the text of a comment.

        Args:
            db (AsyncSession): The database session object for asynchronous database operations.
            comment_id (UUID): The ID of the comment to update.
            new_text (str): The new text for the comment.

        Returns:
            Comment: The updated comment object.

        Raises:
            HTTPException: If the comment is not found (404) or if an error occurs during the update (500).
        """
        try:
            comment = await CommentRepository.get_comment_by_id(db, comment_id)
            if comment:
                comment.text = new_text
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
        """
        Deletes a comment by its ID.

        Args:
            db (AsyncSession): The database session object for asynchronous database operations.
            comment_id (UUID): The ID of the comment to delete.

        Raises:
            HTTPException: If the comment is not found (404) or if an error occurs during the deletion (500).
        """
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
    async def get_comment_by_photo_id(
        db: AsyncSession, photo_id: UUID
    ) -> Sequence[Comment]:
        """
        Retrieves all comments for a given photo ID.

        Args:
            db (AsyncSession): The database session object for asynchronous database operations.
            photo_id (UUID): The ID of the photo to retrieve comments for.

        Returns:
            Sequence[Comment]: A list of comments associated with the photo.
        """
        result = await db.execute(select(Comment).where(Comment.photo_id == photo_id))
        return result.scalars().all()
