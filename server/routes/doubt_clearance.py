"""Doubt Clearance Route"""

from typing import Annotated

from fastapi import (APIRouter,
                     Depends,
                     File,
                     BackgroundTasks,
                     HTTPException,
                     status,
                     UploadFile)

from server.utils.util import generate_response
from server.brain.transcription import generate_transcription_data
from server.utils.current_user import current_user, current_conversation, CurrentUserResponse, CurrentConversationResponse
from server.utils.memory_utils import (add_generated_response_to_memory,
                                       get_conversations_by_user,
                                       delete_conversation_by_id)
from server.brain.image_questions import save_uploaded_image
from server.utils.image_processing import get_image_url
from server.models.conversation import (ChatResponse, 
                                        ConversationMessagesResponse, 
                                        ConversationsListResponse, 
                                        DeleteConversationResponse, 
                                        ConversationClearResponse, 
                                        ChatRequest)
from server.models.images import ImageUploadResponse, ImageDetailsResponse


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

@router.post("/files/image_upload", response_model=ImageUploadResponse)
async def image_upload(file: UploadFile = File(...),
                       user_history: CurrentUserResponse = Depends(current_user),
                       user_token: Annotated[str, None] = None):
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No file uploaded.")
    response = await save_uploaded_image(
        image_file=file,
        user_id=user_history.user.user_id,
        user_token=user_token,
        file_name=file.filename
    )
    if response["status"] == "error":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=response["message"])
    return response

@router.get("/files/uploaded_images/{file_id}", response_model=ImageDetailsResponse)
async def get_uploaded_image(file_id: str):
    response = await get_image_url(file_id)
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Image not found.")
    return response

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

@router.post("/chat", response_model=ChatResponse)
async def doubt_clearance_chat(
    chat_request: ChatRequest,
    user_history: CurrentConversationResponse = Depends(current_conversation),
):
    generated_content, link, total_token = generate_response(
        chat_request.question,
        user_history=user_history,
        course_name=chat_request.course_name,
    )
    if generated_content:
        await add_generated_response_to_memory(
            generated_content,
            link,
            chat_request.question,
            user_history.user,
            total_token,
            conversation_id=user_history.conversation.id
        )
    return {"content": generated_content, "link": link, "conversation_id": str(user_history.conversation.id)}

@router.get("/conversation/{conversation_id}", response_model=ConversationMessagesResponse)
async def get_conversation(
    user_history: CurrentUserResponse = Depends(current_conversation),
):
    conversation_messages = user_history.messages

    return {
        "messages": conversation_messages,
    }

@router.get("/conversations", response_model=ConversationsListResponse)
async def get_all_conversations(
    user_history: CurrentUserResponse = Depends(current_user),
):
    conversations = await get_conversations_by_user(user_history.user)
    return {"conversations": conversations}

@router.delete("/conversation/{conversation_id}", response_model=DeleteConversationResponse)
async def delete_conversation(
    user_history: CurrentUserResponse = Depends(current_conversation),
):
    try:
        response = await delete_conversation_by_id(user_history.conversation)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found or already deleted.") from e

@router.patch("/conversation/clear/{conversation_id}", response_model=ConversationClearResponse)
async def clear_conversation(
    user_history: CurrentConversationResponse = Depends(current_conversation),
):
    if not user_history.conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    for message in user_history.messages:
        message.is_cleared = True
        await message.save()

    return {"detail": "Conversation cleared successfully."}