from contextlib import asynccontextmanager
from typing import AsyncGenerator

import qdrant_client
import redis.asyncio as redis
from qdrant_client import AsyncQdrantClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from ..core.config import get_settings


class DatabaseManager:
    def __init__(self):
        self.settings = get_settings()
        self.engine = None
        self.session_factory = None
        self.redis = None
        self.qdrant = None

    def init_resources(self):
        """应用启动时调用"""
        # MySQL 引擎
        self.engine = create_async_engine(
            self.settings.mysql_url,
            pool_pre_ping=True,  # 每次从池拿连接前先 ping，防止连接失效
            pool_size=20,  # 基础池大小
            max_overflow=10,  # 瞬时高峰额外允许连接数
            pool_recycle=3600,  # 1小时回收连接，防止 MySQL 服务器主动断开
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False,
            class_=AsyncSession,
        )
        # Redis 连接池
        self.redis = redis.from_url(
            self.settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            password=self.settings.redis_password,
            max_connections=100,  # 企业级必设，防止连接泄露耗尽资源
            health_check_interval=30  # 定时心跳，防止防火墙或代理断开连接
        )
        # Qdrant连接
        self.qdrant = AsyncQdrantClient(
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key
        )

    async def close_resources(self):
        """应用关闭时调用"""
        if self.engine:
            await self.engine.dispose()
        if self.redis:
            await self.redis.close()
        if self.qdrant:
            await self.qdrant.close()


# 实例化单例
db_manager = DatabaseManager()


# --- 依赖注入项 ---
@asynccontextmanager
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """数据库 Session 依赖项"""
    async with db_manager.session_factory() as session:
        # 注意：这里不再自动 commit，由 service 层决定是否 commit
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_mysql() -> AsyncGenerator[AsyncSession, None]:
    """数据库 Session 依赖项"""
    async with db_manager.session_factory() as session:
        # 注意：这里不再自动 commit，由 service 层决定是否 commit
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_qdrant() -> AsyncQdrantClient:
    return db_manager.qdrant


async def get_redis() -> redis.Redis:
    """Redis 依赖项"""
    return db_manager.redis
