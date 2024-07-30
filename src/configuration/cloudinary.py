import cloudinary
import cloudinary.uploader
from src.configuration.settings import config
import io


cloudinary.config( 
    cloud_name = config.CLOUDINARY_NAME, 
    api_key = config.CLOUDINARY_API_KEY, 
    api_secret = config.CLOUDINARY_API_SECRET,
    secure=True
)

def upload_qr_to_cloudinary(img, filename):
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr)
    img_byte_arr.seek(0)
    r = cloudinary.uploader.upload(
        img_byte_arr,
        public_id=f'PhotoShare/{filename}',
        overwrite=True
    )
    return cloudinary.CloudinaryImage(f'PhotoShare/{filename}').build_url(
        width=250, height=250, crop='fill', version=r.get('version')
    )