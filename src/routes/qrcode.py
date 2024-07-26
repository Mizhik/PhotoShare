from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.db import get_db
from fastapi import APIRouter, Depends, HTTPException
from src.entity.models import Photo
from src.repository.qr_code import QrCode
from src.schemas.qr_code import QrCreateResponse,QrGetResponse


router = APIRouter(prefix="/generate_qr", tags=["generate_qr"])

@router.post("/generate_qr/{photo_id}", response_model=QrCreateResponse)
async def generate_qr(photo_id: UUID, db: AsyncSession = Depends(get_db)) -> str:
    stmt = select(Photo).filter_by(id = photo_id)
    photo = await db.execute(stmt)
    photo = photo.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    qr_code = await QrCode.generate_qr_code(photo.url, db, photo.id)
    return f'{qr_code}'


@router.get('/get_qr/{photo_id}', response_model=QrGetResponse)
async def get_qr(photo_id: UUID, db: AsyncSession = Depends(get_db)) -> str:
    qr_code = await QrCode.get_qr_code(photo_id, db)
    return {'qr_url': qr_code}
