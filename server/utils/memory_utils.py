from server.models.user import Message, User, Conversation, ImageDetails
from server.utils.util import generate_conversation_title

async def add_generated_response_to_memory(generated_content, link, question,
                                           user: User,
                                           total_token_used: int = None,
                                           search_type: str = None,
                                           conversation: Conversation = None,
                                           image_id: str= None,
                                           image_url: str= None,
                                           image_mime_type: str = None,
                                           thought_summary: str = "",):
    is_message_hidden = False
    if search_type == "subtopic":
        is_message_hidden = True
    image_details = ImageDetails(image_id=image_id, image_url=image_url, image_mime_type=image_mime_type)
    new_message = Message(question=question,
                        image_details= image_details,
                        answer=generated_content,
                        thought_summary=thought_summary,
                        video_url=link,
                        user=user,
                        token_count=total_token_used,
                        is_cleared=is_message_hidden,
                        conversation=conversation
                        )
    await new_message.save()
    user.total_token += total_token_used
    await user.save()
    if conversation:
        if conversation.title == "":
            conversation.title = generate_conversation_title(question,generated_content)
        conversation.updated_at = new_message.created_at
        await conversation.save()

async def get_conversations_by_user(user: User):
    conversations = await Conversation.find(Conversation.user.id == user.id, Conversation.is_deleted == False).to_list()
    return conversations

async def delete_conversation_by_id(conversation: Conversation):
    conversation.is_deleted = True
    await conversation.save()
    return {"conversation_id": str(conversation.id) , "detail": "Conversation deleted successfully."}

async def change_conversation_title(conversation: Conversation, new_title: str):
    conversation.title = new_title
    await conversation.save()
    return {"status":True}