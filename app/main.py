"""FastAPI 应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import connect_mongodb, disconnect_mongodb, connect_redis, disconnect_redis
from app.api.v1.router import api_router

# 配置日志
setup_logging()

# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    """应用启动时连接数据库"""
    # 如果数据库已经连接（测试环境），则跳过
    from app.core.database import mongodb_db, redis_client
    if mongodb_db is None:
        await connect_mongodb()
    if redis_client is None:
        await connect_redis()


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时断开数据库连接"""
    # 只在非测试环境中断开连接（测试环境由 fixture 管理）
    import os
    if os.getenv("MONGODB_DB_NAME") != "fastapi_demo_test":
        await disconnect_mongodb()
    if os.getenv("REDIS_DB") != "1":
        await disconnect_redis()


@app.get("/", tags=["root"])
async def root():
    """根路径"""
    return {
        "message": "Welcome to FastAPI Best Practice",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

