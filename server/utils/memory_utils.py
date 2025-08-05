from beanie.operators import In, Set

from server.models.user import Message, User


async def add_generated_response_to_memory(generated_content, link, question,
                                           user: User,
                                           total_token_used: int = None,
                                           search_type: str = None):
    is_message_hidden = False
    if search_type == "subtopic":
        is_message_hidden = True
    new_message = Message(question=question,
                        answer=generated_content,
                        video_url=link,
                        user=user,
                        token_count=total_token_used,
                        is_cleared=is_message_hidden)
    await new_message.save()
    user.total_token += total_token_used
    await user.save()
    return new_message

async def record_message_rating(message_id, rating):
    message = await Message.find(Message.id == message_id).first_or_none()
    if not message:
        return False
    message.rating = rating if rating != "NULL" else None
    await message.save()
    return True

async def clear_user_message_history(user_history):
    messages_ids = [message.id for message in user_history.messages]
    await Message.find(In(Message.id, messages_ids)).update(Set({Message.is_cleared: True}))
    return True
