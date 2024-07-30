from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.database.db import get_db
from src.schemas.coment import CommentCreate, CommentUpdate, CommentResponse
from src.repository.comment import CommentRepository
from src.entity.models import Role, User
from src.services.decorators import roles_required
from src.repository.user import UserRepository

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
		comment_create: CommentCreate,
		photo_id: UUID,
		db: AsyncSession = Depends(get_db),
		current_user: User = Depends(UserRepository.get_current_user)
) -> CommentResponse:
    comment = await CommentRepository.create_comment(
        db=db, text=comment_create.text, user_id=current_user.id, photo_id=photo_id
    )
    return CommentResponse.model_validate(comment)


@router.get("/{comment_id}", response_model=CommentResponse)
async def read_comment(
		comment_id: UUID,
		db: AsyncSession = Depends(get_db)
) -> CommentResponse:
	comment = await CommentRepository.get_comment_by_id(db, comment_id)
	if not comment:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
	return CommentResponse.model_validate(comment)


@roles_required((Role.admin, Role.moderator, Role.user))
@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
		comment_id: UUID,
		comment_update: CommentUpdate,
		db: AsyncSession = Depends(get_db),
		current_user: User = Depends(UserRepository.get_current_user)
) -> CommentResponse:
	comment = await CommentRepository.get_comment_by_id(db, comment_id)
	if not comment:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

	if not current_user.is_admin and not current_user.is_moderator and current_user.id != comment.user_id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not autorized")
	updated_comment = await CommentRepository.update_comment(db, comment_id, comment_update.text)
	if not updated_comment:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
	return CommentResponse.model_validate(updated_comment)


@roles_required((Role.admin, Role.moderator))
@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
		comment_id: UUID,
		db: AsyncSession = Depends(get_db),
		current_user: User = Depends(UserRepository.get_current_user)
) -> None:
	comment = await CommentRepository.get_comment_by_id(db, comment_id)
	if not comment:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

	if not current_user.is_admin and not current_user.is_moderator:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
	try:
		await CommentRepository.delete_comment(db, comment_id)
	except HTTPException as e:
		raise e


@router.get("/photos/{photo_id}", response_model=list[CommentResponse])
async def get_comments_by_photo(
		photo_id: UUID,
		db: AsyncSession = Depends(get_db)
) -> list[CommentResponse]:
	comments = await CommentRepository.get_comment_by_photo_id(db, photo_id)
	return [CommentResponse.model_validate(comment) for comment in comments]
