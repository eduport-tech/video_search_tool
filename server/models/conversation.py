from pydantic import BaseModel
from server.models.user import Message, Conversation

class ChatRequest(BaseModel):
    question: str
    image_id: str | None = None
    course_name: str = ""

class ChatResponse(BaseModel):
    content: str
    link: str | None
    conversation_id: str

class ConversationMessagesResponse(BaseModel):
    messages: list[Message]

class ConversationsListResponse(BaseModel):
    conversations: list[Conversation]

class DeleteConversationResponse(BaseModel):
    conversation_id: str
    detail: str

class ConversationClearResponse(BaseModel):
    detail: str



