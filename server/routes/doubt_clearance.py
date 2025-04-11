"""Doubt Clearance Route"""

from typing import Annotated

from fastapi import APIRouter, Depends, File

from server.utils.util import generate_response
from server.brain.transcription import generate_transcription_data
from server.utils.current_user import current_user
from server.utils.memory_utils import add_generated_response_to_memory
from server.utils.current_user import CurrentUserResponse


router = APIRouter(tags=["Doubt Clearance"])


@router.get("/ping")
def ping():
    return "PONG"


@router.post("/question")
async def video_search_api(
    question: str,
    type: str = None,
    video_id: int = None,
    course_name: str = "",
    user_history: CurrentUserResponse = Depends(current_user),
):

    if type == "subtopic":
        generated_content, link, total_token = generate_response(
            question,
            video_id=video_id,
            user_history=user_history,
            course_name=course_name,
        )
    else:
        generated_content, link, total_token = generate_response(
            question,
            user_history=user_history,
            course_name=course_name,
        )
    if generated_content:
        await add_generated_response_to_memory(
            generated_content, link, question, user_history.user, total_token
        )
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
    return {"details": "message cleared successfully"}


@router.get("/user-history")
async def get_user_chat_history(
    user_history: CurrentUserResponse = Depends(current_user),
):
    return user_history.messages
