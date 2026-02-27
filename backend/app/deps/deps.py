import json
from fastapi import Depends, HTTPException, status

import redis.asyncio as redis

from backend.app.db.session import get_redis
from backend.app.models.cacheModels import UserInRedis


async def get_current_user(
        token: str,  # 假设 token 是 user_id 或从 JWT 解析出的 ID
        redis_conn: redis.Redis = Depends(get_redis)
) -> UserInRedis:
    # 1. 定义 Key
    user_key = f"user:{token}"

    # 2. 从 Redis 获取数据
    user_data = await redis_conn.get(user_key)

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid"
        )

    # 3. 反序列化为 Pydantic 对象
    return UserInRedis.model_validate_json(user_data)
