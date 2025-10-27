from server.models.user import Message, User, Conversation
from bson import ObjectId

async def add_generated_response_to_memory(generated_content, link, question,
                                           user: User,
                                           total_token_used: int = None,
                                           search_type: str = None,
                                           conversation_id: str = None):
    is_message_hidden = False
    if search_type == "subtopic":
        is_message_hidden = True
    conversation = await Conversation.find(Conversation.id == ObjectId(conversation_id)).first_or_none() if conversation_id else None
    new_message = Message(question=question,
                        answer=generated_content,
                        video_url=link,
                        user=user,
                        token_count=total_token_used,
                        is_cleared=is_message_hidden,
                        conversation=conversation
                        )
    await new_message.save()
    user.total_token += total_token_used
    await user.save()

async def get_conversations_by_user(user: User):
    conversations = await Conversation.find(Conversation.user.id == user.id, Conversation.is_deleted == False).to_list()
    return conversations

async def delete_conversation_by_id(conversation: Conversation):
    conversation.is_deleted = True
    await conversation.save()
    return {"conversation_id": str(conversation.id) , "detail": "Conversation deleted successfully."}