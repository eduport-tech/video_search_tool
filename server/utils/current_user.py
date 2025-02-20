"""Utils function for current logged in users"""
from typing import List

from fastapi import Header, HTTPException
from pydantic import BaseModel, Field

from server.models.user import User, Message

class CurrentUserResponse(BaseModel):
    user: User = Field(description="User Document Item")
    messages: List[Message] = Field(description="List of messages of user")

async def current_user(authorization: str | None = Header(None), x_user_id: str | None = Header(None)) -> CurrentUserResponse:
    print(x_user_id, authorization)
    if x_user_id:
        user_token = None
        if authorization:
            try:
                user_token = authorization.split(' ')[1]
            except IndexError:
                raise HTTPException(status_code=400,
                                    detail="The provided token is invalid")
        user = await User.find(User.user_id==x_user_id).first_or_none()
        if user:
            if user_token and user_token != user.auth_token:
                user.auth_token = user_token
                user.save()
            if not user.is_allowed:
                raise HTTPException(status_code=400,
                                    detail="Your not allowed to access it.")
            user_messages = await Message.find(Message.user.id == user.id,
                                                Message.is_cleared == False)\
                                                    .sort(-Message.created_at)\
                                                    .to_list()
            return CurrentUserResponse(user=user, messages=user_messages)
        else:
            starting_history = User(user_id=x_user_id)
            if user_token:
                starting_history.auth_token = user_token
            return await User.insert_one(starting_history)
    else:
        raise HTTPException(status_code=400,
                            detail="The x-user-id and Authorization is required.")