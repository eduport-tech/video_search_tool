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


CONFIG = Settings()
