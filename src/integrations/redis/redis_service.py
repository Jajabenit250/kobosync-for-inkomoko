# import aioredis

class RedisService:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis = None

    # async def connect(self):
    #     self.redis = await aioredis.create_redis_pool(self.redis_url)

    async def disconnect(self):
        self.redis.close()
        await self.redis.wait_closed()

    # Example operation: set key-value pair
    async def set_value(self, key: str, value: str):
        await self.redis.set(key, value)

    # Example operation: get value by key
    async def get_value(self, key: str) -> str:
        value = await self.redis.get(key, encoding="utf-8")
        return value
