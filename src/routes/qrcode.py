from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from fastapi import APIRouter, Depends, HTTPException
from src.entity.models import Photo
from src.repository.qr_code import QrCode
from src.schemas.qr_code import QrSchema,QrUrl



router = APIRouter(prefix="/generate_qr", tags=["generate_qr"])

@router.post("/generate_qr/{photo_id}", response_model=QrSchema)
def generate_qr(photo_id: int, db: AsyncSession = Depends(get_db)) -> str:
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    qr_code = QrCode.generate_qr_code(photo.url,photo.photo_id)
    return f'{qr_code}'

@router.get('/get_qr/{photo_id}', response_model=QrUrl)
async def get_qr(photo_id: int, db: AsyncSession = Depends(get_db)) -> str:
    qr_code = await QrCode.get_qr_code(photo_id, db)
    return {'qr_url': qr_code}