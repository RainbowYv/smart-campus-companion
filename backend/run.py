from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.queryAgentApi import router as user_router
from app.api.login import login_router
from backend.app.core.config import get_settings
from backend.app.db.session import db_manager

settings = get_settings()


# 使用 lifespan 管理生命周期
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 启动时：初始化所有连接
    db_manager.init_resources()
    print("数据库和 Redis 连接池已初始化")
    print("\n" + "=" * 60)
    print("📚 API文档: http://localhost:8000/docs")
    print("📖 ReDoc文档: http://localhost:8000/redoc")
    print("=" * 60 + "\n")
    yield
    # 2. 关闭时：释放所有资源
    await db_manager.close_resources()
    print("连接池已优雅关闭")


app = FastAPI(lifespan=lifespan, title="校园智能助手")

# 挂载路由
app.include_router(user_router, prefix="/api", tags=["Users"])
app.include_router(login_router, prefix="/api", tags=["login"])

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
