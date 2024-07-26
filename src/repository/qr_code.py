from uuid import UUID
import qrcode
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import QrCode as QrCodeModel
from src.configuration.cloudinary import upload_qr_to_cloudinary

class QrCode:
    @staticmethod
    async def generate_qr_code(url_photo: str, db: AsyncSession, photo_id: UUID) -> str:
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
        transformed_image = QrCodeModel(photo_id=photo_id,qr_code_url=qr_url)
        db.add(transformed_image)
        await db.commit()
        await db.refresh(transformed_image)
        return transformed_image

    @staticmethod
    async def get_qr_code(qr_url: QrCodeModel.qr_code_url, db:AsyncSession) -> str:
        qr = await db.query(QrCodeModel).filter(QrCodeModel.qr_code_url == qr_url).first()
        if qr:
            return qr
        else:
            return 'QR code not found'

qr_repository = QrCode()
