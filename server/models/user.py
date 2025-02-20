from typing import Annotated, Optional, List
from datetime import datetime

from beanie import Document, Indexed, Link
from pydantic import Field

class Message(Document):
    question: str
    answer: str
    video_url: str | None = None
    token_count: int = 0
    is_cleared: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    user: Link["User"] = Field(original_field="messages")


class User(Document):
    """User Data and Message History"""
    user_id: Annotated[str, Indexed(str, unique=True)]
    total_token: int = 0
    is_allowed: bool = True
    auth_token: str = ""
    messages: Optional[List[Link[Message]]] = []

    @property
    def created(self) -> datetime | None:
        """Datetime user was created from ID."""
        return self.id.generation_time if self.id else None