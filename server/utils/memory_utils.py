from server.models.user import Message
from server.utils.current_user import CurrentUserResponse


async def add_generated_response_to_memory(generated_content, link, question, user_history: CurrentUserResponse):
    is_duplicate = False
    for message in user_history.messages:
        if message.question == question and message.answer == generated_content:
            is_duplicate = True
            break
    if not is_duplicate:
        new_message = Message(question=question,
                            answer=generated_content,
                            video_url=link,
                            user=user_history.user)
        await new_message.save()