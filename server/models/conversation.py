from pydantic import BaseModel
from beanie import PydanticObjectId
from typing import Optional
from server.models.user import Conversation, ImageDetails
from datetime import datetime

class MessageResponse(BaseModel):
    id: PydanticObjectId
    question: str
    image_details: Optional[ImageDetails] = None
    answer: str
    video_url: str | None = None
    is_cleared: bool = False
    rating: str | None = None
    created_at: datetime

class ChatRequest(BaseModel):
    question: str = "" 
    image_id: str | None = ""
    course_name: str = ""

class ChatResponse(BaseModel):
    content: str
    link: str | None
    message_id: str
    conversation_id: str

class ConversationMessagesResponse(BaseModel):
    messages: list[MessageResponse]

class ConversationsListResponse(BaseModel):
    conversations: list[Conversation]

class DeleteConversationResponse(BaseModel):
    conversation_id: str
    detail: str

class ConversationClearResponse(BaseModel):
    detail: str

class ConversationRenameResponse(BaseModel):
    success: bool

class MessageRatingResponse(BaseModel):
    details: str