import cloudinary
import cloudinary.uploader
from src.configuration import settings
import io
from PIL import Image

# Configuration       
cloudinary.config( 
    cloud_name = settings.CLOUDINARY_NAME, 
    api_key = settings.CLOUDINARY_API_KEY, 
    api_secret = settings.CLOUDINARY_API_SECRET,
    secure=True
)

def upload_qr_to_cloudinary(img, filename):
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    r = cloudinary.uploader.upload(
        img_byte_arr,
        public_id=f'PhotoShare/{filename}',
        overwrite=True
    )
    
    return cloudinary.CloudinaryImage(f'PhotoShare/{filename}').build_url(
        width=250, height=250, crop='fill', version=r.get('version')
    )