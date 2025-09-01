"""Doubt Clearance Route"""

from typing import Annotated

from fastapi import (APIRouter,
                     Depends,
                     File,
                     BackgroundTasks,
                     HTTPException,
                     status)

from server.utils.util import generate_response
from server.brain.transcription import generate_transcription_data
from server.utils.current_user import current_user
from server.utils.memory_utils import add_generated_response_to_memory
from server.utils.current_user import CurrentUserResponse
from server.services.redis_cache import redis_dep, get_class


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
    r = Depends(redis_dep) 
):

    class_info = await get_class(r,course_name)
    print(class_info)
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
            class_info=class_info,
        )
    if generated_content:
        await add_generated_response_to_memory(
            generated_content, link, question, user_history.user, total_token
        )
    return {"content": generated_content, "link": link}


@router.post("/audio")
async def audio_transcription(audio_data: Annotated[bytes, File()],
                              background_tasks: BackgroundTasks,
                              user_id: Annotated[str, None] = None,
                              user_token: Annotated[str, None] = None):
    transcription = await generate_transcription_data(audio_data,
                                                      background_tasks,
                                                      user_id=user_id,
                                                      user_token=user_token)
    if not transcription:
        return HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                             detail="Maximum audio length reached.")
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
