"""Utils function for current logged in users"""

from typing import List
from datetime import datetime, date

from fastapi import Header, HTTPException
from pydantic import BaseModel, Field

from server.models.user import User, Message, MessageView
from server.config import CONFIG


class CurrentUserResponse(BaseModel):
    user: User = Field(description="User Document Item")
    messages: List[MessageView] = Field(description="List of messages of user")


async def current_user(
    authorization: str | None = Header(None),
    x_user_id: str | None = Header(None),
    x_is_premium: bool | None = Header(False),
) -> CurrentUserResponse:
    if x_user_id:
        user = await User.find(User.user_id == x_user_id).first_or_none()
        if user:
            _ = await handle_user_limits(user)
            _ = await update_user_details(
                user=user, is_premium=x_is_premium, authorization=authorization
            )
            user_messages = await get_user_active_messages(user)
            return CurrentUserResponse(user=user, messages=user_messages)
        else:
            starting_history = User(user_id=x_user_id)
            auth_token = await make_auth_token(authorization) if authorization else ""
            starting_history.auth_token = auth_token
            await User.insert_one(starting_history)
            return CurrentUserResponse(user=starting_history, messages=[])
    else:
        raise HTTPException(
            status_code=400, detail="The x-user-id and Authorization is required."
        )


async def get_todays_message_count(user_id):
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    message_count = await Message.find(
        Message.user.id == user_id,
        Message.created_at >= today_start,
        Message.created_at <= today_end,
    ).count()
    return message_count


async def handle_user_limits(user: User) -> bool:
    if not user.is_allowed:
        raise HTTPException(status_code=400, detail="Your input violates our guidelines. Please modify and try again.")
    if user.is_premium and user.total_token > CONFIG.premium_token_limit:
        raise HTTPException(status_code=429, detail="Maximum token limit reached")
    elif user.total_token > CONFIG.normal_token_limit:
        raise HTTPException(status_code=429, detail="Maximum token limit reached")
    today_message_count = await get_todays_message_count(user.id)
    if user.is_premium:
        if today_message_count + 1 >= CONFIG.premium_message_pre_day:
            raise HTTPException(status_code=429, detail="You've reached today's question limit! You can ask more questions tomorrow.")
    elif today_message_count + 1 >= CONFIG.normal_message_pre_day:
        raise HTTPException(status_code=429, detail="You've reached today's question limit! You can ask more questions tomorrow.")
    return False


async def update_user_details(user: User, is_premium: bool, authorization: str = None):
    if authorization:
        authorization = await make_auth_token(authorization)
        if authorization and authorization != user.auth_token:
            user.auth_token = authorization
    if is_premium is not None and user.is_premium != is_premium:
        user.is_premium = is_premium
    await user.save()
    return True


async def make_auth_token(authorization: str):
    try:
        authorization = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(status_code=400, detail="The provided token is invalid")
    return authorization


async def get_user_active_messages(user: User):
    pipeline = [
        {"$match": {"user.$id": user.id, "is_cleared": False}},
        {"$sort": {"created_at": -1}},
        {"$addFields": {"_id": "$_id", "id": "$_id"}},
        {"$project": {"user": 0}}
    ]
    user_messages_docs = await Message.aggregate(pipeline).to_list()
    return [MessageView(**message) for message in user_messages_docs]
