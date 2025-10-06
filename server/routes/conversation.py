"""Conversation Route"""

from fastapi import (APIRouter,
                     Depends,
                     HTTPException,
                     status,)
from beanie import PydanticObjectId
from typing import Literal

from server.utils.util import generate_image_response
from server.utils.current_user import current_conversation_user, CurrentUser
from server.utils.current_conversation import current_conversation, create_conversation, CurrentConversation
from server.utils.memory_utils import (add_generated_response_to_memory,
                                       get_conversations_by_user,
                                       delete_conversation_by_id,
                                       change_conversation_title,
                                       record_message_rating,
                                       clear_conversation_messages,)
from server.utils.image_processing import get_image_url
from server.models.conversation import (ChatResponse, 
                                        ConversationMessagesResponse, 
                                        ConversationsListResponse, 
                                        DeleteConversationResponse, 
                                        ConversationClearResponse, 
                                        ChatRequest,
                                        MessageRatingResponse,
                                        ConversationRenameResponse)


router = APIRouter(tags=["Conversation"])


@router.post("/chat", response_model=ChatResponse)
async def doubt_clearance_chat(
    chat_request: ChatRequest,
    current_user: CurrentUser = Depends(current_conversation_user),
    current_conversation: CurrentConversation = Depends(current_conversation),
):
    image_url, image_mime_type = None, None
    if chat_request.image_id:
        image = await get_image_url(chat_request.image_id)
        image_url = image.url
        image_mime_type = image.mime_type
    generated_content, thought, link, total_token = await generate_image_response(
        chat_request.question,
        image_url=image_url,
        image_mime_type=image_mime_type,
        user_history=current_conversation,
        course_name=chat_request.course_name,
    )
    if generated_content:
        if not current_conversation.conversation:
            current_conversation.conversation = await create_conversation(user=current_user)
        message = await add_generated_response_to_memory(
            generated_content,
            link,
            chat_request.question,
            current_user,
            total_token,
            conversation=current_conversation.conversation,
            image_id=chat_request.image_id,
            image_url=image_url,
            image_mime_type=image_mime_type,
            thought_summary=thought,
        )
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to generate response.")
    return {"content": generated_content,
            "link": link,
            "message_id": str(message.id),
            "conversation_id": str(current_conversation.conversation.id)}


@router.get("/conversation/{conversation_id}",
            dependencies=[Depends(current_conversation_user)],
            response_model=ConversationMessagesResponse)
async def get_conversation(
    current_conversation: CurrentConversation = Depends(current_conversation),
):
    conversation_messages = current_conversation.messages
    return {
        "messages": conversation_messages,
    }


@router.get("/conversations", response_model=ConversationsListResponse)
async def get_all_conversations(
    current_user: CurrentUser = Depends(current_conversation_user),
):
    conversations = await get_conversations_by_user(current_user)
    return {"conversations": conversations}


@router.delete("/conversation/{conversation_id}",
                dependencies=[Depends(current_conversation_user)],
                response_model=DeleteConversationResponse)
async def delete_conversation(
    current_conversation: CurrentConversation = Depends(current_conversation),
):
    try:
        response = await delete_conversation_by_id(current_conversation.conversation)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found or already deleted.") from e


@router.patch("/conversation/clear/{conversation_id}",
              dependencies=[Depends(current_conversation_user)],
              response_model=ConversationClearResponse)
async def clear_conversation(
    current_conversation: CurrentConversation = Depends(current_conversation),
):
    if not current_conversation.conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    await clear_conversation_messages(current_conversation)

    return {"detail": "Conversation cleared successfully."}


@router.patch("/conversation/rename/{conversation_id}",
                dependencies=[Depends(current_conversation_user)], response_model=ConversationRenameResponse)
async def rename_conversation(current_conversation: CurrentConversation = Depends(current_conversation),
                              new_title: str = ""):
    if not current_conversation.conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    await change_conversation_title(current_conversation.conversation, new_title)
    return {"success": True}


@router.post("/message-rating", dependencies=[Depends(current_conversation_user)], response_model=MessageRatingResponse)
async def post_message_rating(
    message_id: str,
    rating: Literal["LIKE", "DISLIKE", "NULL"]
):
    try:
        message_id = PydanticObjectId(message_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid message ID format")

    completed = await record_message_rating(message_id, rating)
    if not completed:
        return HTTPException(status_code=404, detail="Message not found")
    return {"details": "rating posted successfully"}