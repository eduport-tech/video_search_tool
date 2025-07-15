from uuid import uuid4
import logging

import boto3

from google.genai.types import (
    GenerateContentResponse,
    GenerateContentResponseUsageMetadata
)

from server.models.user import User, AudioData
from server.config import CONFIG

logger = logging.getLogger(__name__)

async def save_audio_to_r2(audio_file, extension, file_name):
    """
    Uploads an audio file to Cloudflare R2 and returns the public URL.
    """
    try:
        s3 = boto3.client("s3",
                          endpoint_url=CONFIG.r2_endpoint_url,
                          aws_access_key_id=CONFIG.r2_access_key_id,
                          aws_secret_access_key=CONFIG.r2_secret_access_key,
                          region_name="auto",)
        bucket_name = CONFIG.r2_bucket_name
        s3.put_object(Bucket=bucket_name, Key=f"{file_name}{extension}", Body=audio_file)
        return f"{CONFIG.r2_public_url}/{bucket_name}/{file_name}{extension}"
    except Exception as e:
        logger.error(f"Error uploading to R2: {e}")
        return None

async def record_audio_input(audio_file, file_type, user_id, user_token, extension, response: GenerateContentResponse):
    file_name = uuid4()
    uploaded_url = await save_audio_to_r2(
        audio_file=audio_file,
        extension=extension,
        file_name=file_name,
    )
    user = await User.find(User.user_id==user_id).first_or_none() if user_id else None
    usage_metadata:GenerateContentResponseUsageMetadata = response.usage_metadata
    total_token_used:int = usage_metadata.total_token_count
    audio_data = AudioData(
        url=uploaded_url,
        usage_data=usage_metadata.model_dump(),
        total_token_used=total_token_used,
        file_type=file_type,
        transcribed_text=response.text,
        user=user
    )
    await audio_data.save()
    if user:
        user.total_token += total_token_used
        await user.save()