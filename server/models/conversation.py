from pydantic import BaseModel
from server.models.user import User, Message, Conversation

class chatRequest(BaseModel):
    question: str
    course_name: str = ""



class ChatResponse(BaseModel):
    content: str
    link: str | None
    conversation_id: str

class ConversationMessages(BaseModel):
    messages: list[Message]

class ConversationsList(BaseModel):
    conversations: list[Conversation]

class DeleteConversationResponse(BaseModel):
    detail: str

class ConversationClearResponse(BaseModel):
    detail: str



