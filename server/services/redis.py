from redis.asyncio import Redis
from fastapi import Request
from redis import ConnectionError, RedisError, TimeoutError
from redis.asyncio.retry import Retry
from redis.backoff import default_backoff

from server.config import CONFIG

REDIS_RETRY_ON_ERRROR: list[type[RedisError]] = [ConnectionError, TimeoutError]
REDIS_RETRY = Retry(default_backoff(), retries=50)

def create_redis_client() -> Redis:
    return Redis(
        host=CONFIG.redis_host,
        port=CONFIG.redis_port,
        decode_responses=True,
        retry_on_error=REDIS_RETRY_ON_ERRROR,
        retry=REDIS_RETRY,
    )

def redis_dep(req: Request):
    return req.app.state.redis