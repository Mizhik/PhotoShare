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
    """
    Generate a QR code for a specific photo.

    **Path Parameters:**

    - `photo_id` (UUID): The ID of the photo for which the QR code is to be generated.

    **Dependencies:**

    - `db` (AsyncSession): The database session for async operations.

    **Responses:**

    - **200 OK**: Returns a `QrCreateResponse` containing the URL of the generated QR code.

    **Raises:**

    - `HTTPException` with status code `404 Not Found` if the photo with the given ID does not exist.


    """
    stmt = select(Photo).filter_by(id=photo_id)
    photo = await db.execute(stmt)
    photo = photo.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return await QrCode.generate_qr_code(photo.url, db, photo.id)


@router.get('/get_qr/{photo_id}', response_model=QrGetResponse)
async def get_qr(photo_id: UUID, db: AsyncSession = Depends(get_db)) -> str:
    """
    Retrieve the QR code URL for a specific photo.

    **Path Parameters:**

    - `photo_id` (UUID): The ID of the photo for which the QR code is to be retrieved.

    **Dependencies:**

    - `db` (AsyncSession): The database session for async operations.

    **Responses:**

    - **200 OK**: Returns a `QrGetResponse` containing the URL of the QR code.

    **Raises:**

    - `HTTPException` with status code `404 Not Found` if the QR code for the photo with the given ID does not exist.

    **Example Response:**


    """
    return await QrCode.get_qr_code(photo_id, db)
