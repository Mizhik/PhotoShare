import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from src.configuration import settings

# Configuration       
cloudinary.config( 
    cloud_name = settings.CLOUDINARY_NAME, 
    api_key = settings.CLOUDINARY_API_KEY, 
    api_secret = settings.CLOUDINARY_API_SECRET,
    secure=True
)

def upload_qr_to_cloudinary(qr_obj, filename):
    r = cloudinary.uploader.upload(
        qr_obj, public_id=f'PhotoShare/{filename}', overwrite=True
        )
    return cloudinary.CloudinaryImage(
        f'PhotoShare/{filename}').build_url(
            width=250, height=250, crop='fill', version=r.get('version')
        )