from server.utils.image_processing import save_image_details, save_image_to_r2
from uuid import uuid4
import os
import logging
logger = logging.getLogger(__name__)

async def save_uploaded_image(image_file, user_id, user_token, file_name):
    try:
        mime_type = image_file.content_type
        content = await image_file.read()

        _, extension = os.path.splitext(file_name)
        r2_file_name = uuid4()
        url = await save_image_to_r2(content, extension, r2_file_name)
        
        file_id = await save_image_details(content, user_id, file_name, url, mime_type)
        
        return {"status": "success", "url": url, "file_id": file_id}
        
    except Exception as e:
        logger.error(f"Error saving uploaded image: {e}")
        return {"status": "error", "message": "Failed to save image."}
    