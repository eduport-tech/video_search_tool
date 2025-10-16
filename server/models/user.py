from typing import Annotated, Optional, List, Literal
from datetime import datetime

from beanie import Document, Indexed, Link, PydanticObjectId
from pydantic import Field, BaseModel


class ImageDetails(BaseModel):
    image_id: Optional[str] = None 
    image_url: Optional[str] = None
    image_mime_type: Optional[str] = None

class Message(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    question: str
    image_details: Optional[ImageDetails] = None
    answer: str
    thought_summary: str = ""
    video_url: str | None = None
    token_count: int = 0
    is_cleared: bool = False
    rating: Literal["LIKE", "DISLIKE", None] = None
    created_at: datetime = Field(default_factory=datetime.now)
    conversation: Optional[Link["Conversation"]] = None
    user: Link["User"] = Field(original_field="messages")

class Conversation(Document):
    """Conversation Session Details"""
    title: str = ""
    is_deleted: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    user: Link["User"]

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

class ImageData(Document):
    original_file_name: str = ""
    is_allowed: bool = True
    is_deleted: bool = False
    url: str
    mime_type: str = ""
    file_size: int = 0
    width: Optional[int] = None
    height: Optional[int] = None
    token_usage: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    user: Link["User"] = Field(original_field="images")

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
