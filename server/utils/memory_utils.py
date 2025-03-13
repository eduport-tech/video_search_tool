from server.models.user import Message, User
from server.utils.current_user import CurrentUserResponse
from typing import List


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