from uuid import UUID
import qrcode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import QrCode as QrCodeModel
from src.configuration.cloudinary import upload_qr_to_cloudinary

class QrCode:
    @staticmethod
    async def generate_qr_code(url_photo: str, db: AsyncSession, photo_id: UUID) -> str:
        """
        Generates a QR code for a given photo URL and stores it in the database.

        Args:
            url_photo (str): The URL of the photo for which the QR code is to be generated.
            db (AsyncSession): The database session object for asynchronous database operations.
            photo_id (UUID): The ID of the photo for which the QR code is generated.

        Returns:
            QrCodeModel: The QR code model object containing the generated QR code URL.

        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url_photo)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        qr_url = upload_qr_to_cloudinary(img, photo_id)
        transformed_image = QrCodeModel(photo_id=photo_id, qr_code_url=qr_url)
        db.add(transformed_image)
        await db.commit()
        await db.refresh(transformed_image)
        return transformed_image

    @staticmethod
    async def get_qr_code(photo_id: str, db:AsyncSession) -> str:
        """
        Retrieves a QR code by photo ID.

        Args:
            photo_id (UUID): The ID of the photo associated with the QR code.
            db (AsyncSession): The database session object for asynchronous database operations.

        Returns:
            QrCodeModel: The QR code model object if found, otherwise None.
        """
        stmt = select(QrCodeModel).filter_by(photo_id=photo_id)
        qr = await db.execute(stmt)
        qr = qr.scalars().first()
        return qr

qr_repository = QrCode()
