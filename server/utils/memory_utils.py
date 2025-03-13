from server.models.user import Message, User
from server.utils.current_user import CurrentUserResponse
from typing import List


async def add_generated_response_to_memory(generated_content, link, question,
                                           user: User,
                                           total_token_used: int = None,
                                           is_hint: bool = False):
    new_message = Message(question=question,
                        answer=generated_content,
                        video_url=link,
                        user=user,
                        token_count=total_token_used,
                        is_hint=is_hint)
    await new_message.save()
    user.total_token += total_token_used
    await user.save()

def get_conversation_history_for_hint_mode(user_history: User) -> str:
    """
    This function retrieves the conversation history starting from the last non-hint message.
    It returns the formatted conversation history as a string.
    """
    # Find the last message where is_hint is False
    last_non_hint_message = None
    for message in reversed(user_history.messages):
        if not message.is_hint:
            last_non_hint_message = message
            break
    # print("History", user_history.messages)
    # print("Last Message", last_non_hint_message)
    
    # If such a message exists, gather history from that point onward
    conversation_history = []
    if last_non_hint_message:
        for message in user_history.messages:
            if message.created_at >= last_non_hint_message.created_at:
                conversation_history.append({
                    "question": message.question,
                    "answer": message.answer
                })
    else:
        # If no non-hint message exists, treat the current question as new context
        conversation_history = []
    
    # Return the formatted conversation history as a string
    return conversation_history