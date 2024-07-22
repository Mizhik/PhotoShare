from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from fastapi import APIRouter, Depends, HTTPException
from src.entity.models import Photo
from src.repository.qr_code import QrCode



router = APIRouter(prefix="/generate_qr", tags=["generate_qr"])

@router.get("/generate_qr/{photo_id}")
async def generate_qr(photo_id: int, db: AsyncSession = Depends(get_db)):
    photo = await db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    qr_code = await QrCode.generate_qr_code(photo.url,photo.photo_id)
    return f'{qr_code}'

