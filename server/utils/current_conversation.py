from typing import List
from bson import ObjectId
from fastapi import Header, HTTPException
from pydantic import BaseModel, Field

from server.models.user import User, Message, Conversation

class CurrentConversation(BaseModel):
    messages: List[Message] = Field(description="List of messages in the conversation")
    conversation: Conversation | None = Field(description="Conversation Document Item")

async def current_conversation(
        x_user_id: str = Header(...),
        conversation_id: str = None,
        x_is_premium: bool | None = Header(False),
):
    user = await User.find(User.user_id == x_user_id).first_or_none()

    if not conversation_id:
        conversation = None
        user_messages = []
    else:
        conversation = await Conversation.find(Conversation.id == ObjectId(conversation_id),
                                               Conversation.user.id == user.id).first_or_none()
        if not conversation or conversation.is_deleted:
            raise HTTPException(status_code=404, detail="Conversation not found.")
        user_messages = await get_conversation_messages(conversation_id, user)
    return CurrentConversation(messages=user_messages, conversation=conversation)

async def get_conversation_messages(conversation_id: str, user: User):
    conversation_messages = (
        await Message.find(
            Message.conversation.id == ObjectId(conversation_id),
            Message.is_cleared == False,
            )
        .sort(-Message.created_at)
        .to_list()
    )
    return conversation_messages or []

async def create_conversation(user: User, title: str = ""):
    conversation = Conversation(
        title=title,
        user=user,
        is_deleted=False
    )
    await conversation.save()
    return conversation