"""Redis client module."""

import aioredis


async def init_redis_pool(url: str) -> aioredis.Redis:
    return aioredis.from_url(url, decode_responses=True)
