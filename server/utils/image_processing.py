from server.models.user import User, ImageData
from PIL import Image as PILImage
from io import BytesIO
import boto3
from server.config import CONFIG
import logging
from bson import ObjectId
from server.models.images import ImageDetailsResponse
logger = logging.getLogger(__name__)

async def save_image_to_r2(image_file, extension, file_name):
    """
    Uploads an image file to Cloudflare R2 and returns the public URL.
    """
    try:
        
        s3 = boto3.client("s3",
                          endpoint_url=CONFIG.r2_endpoint_url,
                          aws_access_key_id=CONFIG.r2_access_key_id,
                          aws_secret_access_key=CONFIG.r2_secret_access_key,
                          region_name="auto",)
        bucket_name = CONFIG.r2_image_bucket_name
        s3.put_object(Bucket=bucket_name, Key=f"{file_name}{extension}", Body=image_file)
        return f"{CONFIG.r2_public_url}/{bucket_name}/{file_name}{extension}"
    except Exception as e:
        logger.error(f"Error uploading to R2: {e}")
        return None

async def save_image_details(image_file, user_id, file_name, url, mime_type):
    """
    Add image details to the database.
    """
    
    image = PILImage.open(BytesIO(image_file))
    width, height = image.size
    user = await User.find(User.user_id == user_id).first_or_none() if user_id else None
    image = ImageData(
        original_file_name=file_name,
        url = url,
        mime_type=mime_type,
        file_size= len(image_file),
        width=width,
        height=height,
        user=user,
    )
    await image.save()
    return str(image.id)

async def get_image_url(file_id: str):
    """
    Retrieve the image details from the database using file_id.
    """
    image = await ImageData.find(ImageData.id == ObjectId(file_id)).first_or_none()
    response = None
    if image:
        response = ImageDetailsResponse.from_image_data(image)
    return response