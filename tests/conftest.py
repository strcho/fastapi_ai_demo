"""测试配置和 fixtures"""
import pytest
import pytest_asyncio
import os
import asyncio
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis

from app.main import app
import app.core.database as db_module


# 设置测试环境变量
os.environ["MONGODB_DB_NAME"] = "fastapi_demo_test"
os.environ["REDIS_DB"] = "1"  # 使用不同的 Redis DB


@pytest_asyncio.fixture(scope="function")
async def client():
    """异步测试客户端 fixture"""
    # 连接测试数据库
    test_mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    test_db_name = os.getenv("MONGODB_DB_NAME", "fastapi_demo_test")
    
    # 创建测试 MongoDB 客户端
    test_mongodb_client = AsyncIOMotorClient(test_mongodb_url)
    test_db = test_mongodb_client[test_db_name]
    
    # 创建测试 Redis 客户端
    test_redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    test_redis_db = int(os.getenv("REDIS_DB", "1"))
    
    test_redis_client = Redis.from_url(
        test_redis_url,
        db=test_redis_db,
        decode_responses=True
    )
    
    # 保存原始值
    original_mongodb_db = db_module.mongodb_db
    original_redis_client = db_module.redis_client
    original_mongodb_client = db_module.mongodb_client
    
    # 设置测试数据库
    db_module.mongodb_db = test_db
    db_module.redis_client = test_redis_client
    db_module.mongodb_client = test_mongodb_client
    
    # 清理测试数据库（在测试前）
    try:
        await test_db.drop_collection("items")
    except Exception:
        pass
    try:
        await test_db.drop_collection("counters")
    except Exception:
        pass
    try:
        await test_redis_client.flushdb()
    except Exception:
        pass
    
    # 创建异步测试客户端
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        try:
            yield test_client
        finally:
            # 测试后清理
            try:
                await test_db.drop_collection("items")
            except Exception:
                pass
            try:
                await test_db.drop_collection("counters")
            except Exception:
                pass
            try:
                await test_redis_client.flushdb()
            except Exception:
                pass
            try:
                await test_redis_client.aclose()
            except Exception:
                pass
            
            # 恢复原始值
            db_module.mongodb_db = original_mongodb_db
            db_module.redis_client = original_redis_client
            db_module.mongodb_client = original_mongodb_client
            
            # 关闭 MongoDB 连接
            try:
                test_mongodb_client.close()
            except Exception:
                pass
