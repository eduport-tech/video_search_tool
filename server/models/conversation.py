from pydantic import BaseModel
from server.models.user import Conversation, ImageDetails
from datetime import datetime

class MessageResponse(BaseModel):
    question: str
    image_details: ImageDetails
    answer: str
    video_url: str | None = None
    is_cleared: bool = False
    created_at: datetime

class ChatRequest(BaseModel):
    question: str = "" 
    image_id: str = ""
    course_name: str = ""

class ChatResponse(BaseModel):
    content: str
    link: str | None
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