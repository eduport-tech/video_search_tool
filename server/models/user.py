from typing import Annotated, Optional, List, Literal
from datetime import datetime

from beanie import Document, Indexed, Link, PydanticObjectId
from pydantic import Field, BaseModel, ConfigDict


class Message(Document):
    question: str
    answer: str
    video_url: str | None = None
    token_count: int = 0
    is_cleared: bool = False
    rating: Literal["LIKE", "DISLIKE", None] = None
    created_at: datetime = Field(default_factory=datetime.now)
    user: Link["User"] = Field(original_field="messages")


class AudioData(Document):
    """User Audio Data Details"""
    url: str = ""
    is_allowed: bool = True
    is_deleted: bool = False
    usage_data: dict = {}
    file_type: str = ""
    transcribed_text: str = ""
    total_token_used: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    user: Link["User"] = Field(original_filed="audios")

class User(Document):
    """User Data and Message History"""

    user_id: Annotated[str, Indexed(str, unique=True)]
    total_token: int = 0
    is_allowed: bool = True
    auth_token: str = ""
    is_premium: bool = False

    messages: Optional[List[Link[Message]]] = []

    @property
    def created(self) -> datetime | None:
        """Datetime user was created from ID."""
        return self.id.generation_time if self.id else None


class MessageView(BaseModel):
    _id: PydanticObjectId #Added for backward compatibility remove after new version
    id: PydanticObjectId
    question: str
    answer: str
    video_url: str | None = None
    token_count: int = 0
    is_cleared: bool = False
    rating: Literal["LIKE", "DISLIKE", None] = None
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )