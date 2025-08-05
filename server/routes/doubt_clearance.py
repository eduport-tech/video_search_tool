"""Doubt Clearance Route"""

from typing import Annotated, Literal

from fastapi import (APIRouter,
                     Depends,
                     File,
                     BackgroundTasks,
                     HTTPException,
                     status,)
from beanie import PydanticObjectId

from server.utils.util import generate_response
from server.brain.transcription import generate_transcription_data
from server.utils.current_user import current_user
from server.utils.memory_utils import (add_generated_response_to_memory,
                                       record_message_rating,
                                       clear_user_message_history,)
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
        message = await add_generated_response_to_memory(
            generated_content, link, question, user_history.user, total_token
        )
    return {"content": generated_content, "link": link, "id": str(message.id)}


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
        await clear_user_message_history(user_history)
    return {"details": "message cleared successfully"}


@router.get("/user-history")
async def get_user_chat_history(
    user_history: CurrentUserResponse = Depends(current_user),
):
    return user_history.messages


@router.post("/message-rating")
async def post_message_rating(
    message_id: str,
    rating: Literal["LIKE", "DISLIKE", "NULL"],
    user_history: CurrentUserResponse = Depends(current_user),
):
    try:
        message_id = PydanticObjectId(message_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid message ID format")
    
    completed = await record_message_rating(message_id, rating)
    if not completed:
        return HTTPException(status_code=404, detail="Message not found")
    return {"details": "rating posted successfully"}
