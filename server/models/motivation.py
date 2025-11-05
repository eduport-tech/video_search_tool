from typing import Optional
from datetime import datetime

from beanie import Document
from pydantic import Field

class Motivation(Document):
    video_url: str
    audio_url: Optional[str] = None
    class_name: str
    teacher_name: str
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
