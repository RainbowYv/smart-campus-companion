import redis
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_redis, get_mysql
from backend.app.models.frontModels import LoginInfo
from backend.app.models.tableModels import Student, Teacher
from backend.app.models.cacheModels import UserInRedis

login_router = APIRouter()


@login_router.post("/login")
async def login(
        user_login: LoginInfo,
        db_redis: redis.Redis = Depends(get_redis),
        db_mysql: AsyncSession = Depends(get_mysql)
):
    stmt = select(Student).where(Student.student_number == user_login.number)
    user = await db_mysql.execute(stmt)
    user = user.scalars().first()
    user_info = UserInRedis()
    user_info.role = "student"
    if not user:
        user_info.role = "teacher"
        stmt = select(Teacher).where(Teacher.employee_number == user_login.number)
        user = await db_mysql.execute(stmt)
        user = user.scalars().first()
    if user.password_hash != user_login.password:
        return "密码错误"
    user_info = UserInRedis.model_validate(user)
    await db_redis.setex(
        f"user:{user_info.number}",
        3600,
        user_info.model_dump_json()
    )
    return user_info
