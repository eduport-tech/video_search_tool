from server.models.user import Message, User
from server.utils.current_user import CurrentUserResponse
from typing import List


async def add_generated_response_to_memory(generated_content, link, question,
                                           user: User,
                                           total_token_used: int = None):
    new_message = Message(question=question,
                        answer=generated_content,
                        video_url=link,
                        user=user,
                        token_count=total_token_used,)
    await new_message.save()
    user.total_token += total_token_used
    await user.save()