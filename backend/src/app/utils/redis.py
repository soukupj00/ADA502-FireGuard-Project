import os

import redis.asyncio as redis

from config import settings

redis_client = redis.from_url(os.getenv("REDIS_URL", settings.REDIS_URL))


async def get_redis_client():
    """Returns the Redis client."""
    return redis_client
