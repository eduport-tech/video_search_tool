"""Doubt Clearance Route"""
from typing import Annotated

from fastapi import APIRouter, Depends, File

from server.utils.util import generate_response, hint_mode_response
from server.brain.transcription import generate_transcription_data
from server.utils.current_user import current_user
from server.utils.memory_utils import add_generated_response_to_memory, get_conversation_history_for_hint_mode
from server.utils.current_user import CurrentUserResponse


router = APIRouter(tags=["Doubt Clearance"])

@router.get("/ping")
def ping():
    return "PONG"

@router.post("/question")
async def video_search_api(question: str, 
                            user_history: CurrentUserResponse = Depends(current_user),
                            hint_mode_enabled: bool = False):  # The switch for Hint Mode
    # Initialize variables for hint mode response
    link = None
    is_hint = False  # Default is no hint
    
    # If hint_mode_enabled is True, find the last non-hint message and gather history from that point
    if hint_mode_enabled:
        # Get the conversation history starting from the last non-hint message
        conversation_history_str = await get_conversation_history_for_hint_mode(user_history.user)
        
        generated_content, total_token = hint_mode_response(question, user_history=conversation_history_str)
        
        is_hint = True  # Mark as hint mode response
    
    else:
        # If not in hint mode, use the regular response generation function
        generated_content, link, total_token = generate_response(question, user_history=user_history)
    
    # Add the generated response to the memory (with the appropriate is_hint flag)
    if generated_content:
        await add_generated_response_to_memory(generated_content,
                                               link, question,
                                               user_history.user,
                                               total_token, 
                                               is_hint=is_hint)  # Pass is_hint here
    
    return {"content": generated_content, "link": link}


@router.post("/audio")
def audio_transcription(audio_data: Annotated[bytes, File()]):
    transcription = generate_transcription_data(audio_data)
    return transcription


@router.post("/clear-history", status_code=200)
async def clear_user_history(user_history: CurrentUserResponse = Depends(current_user)):
    if user_history.user:
        for message in user_history.messages:
            message.is_cleared = True
            await message.save()
    return {"details":"message cleared successfully"}


@router.get("/user-history")
async def get_user_chat_history(user_history: CurrentUserResponse = Depends(current_user)):
    return user_history.messages