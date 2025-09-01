from redis.asyncio import Redis
from fastapi import Request

def redis_dep(req: Request):
    return req.app.state.redis

async def get_class(r: Redis, course_name: str):
    key = f"course_{course_name}"
    data = await r.hgetall(key)
    return data.get("class","")
