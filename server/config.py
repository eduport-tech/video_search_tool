from decouple import config
from pydantic import BaseModel


class Settings(BaseModel):
    "Server Config Class"

    root_url: str = config("ROOT_URL", default="http://localhost:8000")
    mongo_uri: str = config("MONGODB_URL")
    environment: str = config("ENVIRONMENT", default="DEV")
    normal_token_limit: float = float(
        config("NORMAL_TOKEN_LIMIT", default=float("inf"))
    )
    premium_token_limit: float = float(
        config("PREMIUM_TOKEN_LIMIT", default=float("inf"))
    )
    premium_message_pre_day: float = float(
        config("PREMIUM_MESSAGE_PRE_DAY", default=float("inf"))
    )
    normal_message_pre_day: float = float(
        config("NORMAL_MESSAGE_PRE_DAY", default=float("inf"))
    )
    max_audio_token_limit: int = int(
        config("MAX_AUDIO_LIMIT", default=10) * 1920
    )
    max_image_tokens: float = float(
        config("MAX_IMAGE_LIMIT", default=float("inf"))
    )
    gemini_model_name: str = config("GEMINI_MODEL_NAME", default="gemini-2.0-flash")
    r2_endpoint_url: str = config("R2_ENDPOINT_URL")
    r2_access_key_id: str = config("R2_ACCESS_KEY_ID")
    r2_secret_access_key: str = config("R2_SECRET_ACCESS_KEY")
    r2_bucket_name: str = config("R2_BUCKET_NAME")
    r2_image_bucket_name: str = config("R2_IMAGE_BUCKET_NAME", default="user_images")
    r2_public_url: str = config("R2_PUBLIC_URL")


CONFIG = Settings()
