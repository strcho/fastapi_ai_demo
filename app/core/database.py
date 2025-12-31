"""数据库连接模块"""
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# MongoDB 客户端
mongodb_client: Optional[AsyncIOMotorClient] = None
mongodb_db = None

# Redis 客户端
redis_client: Optional[Redis] = None


async def connect_mongodb():
    """连接 MongoDB"""
    global mongodb_client, mongodb_db
    try:
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb_db = mongodb_client[settings.MONGODB_DB_NAME]
        # 测试连接
        await mongodb_client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def disconnect_mongodb():
    """断开 MongoDB 连接"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("Disconnected from MongoDB")


async def connect_redis():
    """连接 Redis"""
    global redis_client
    try:
        redis_client = Redis.from_url(
            settings.REDIS_URL,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        # 测试连接
        await redis_client.ping()
        logger.info(f"Connected to Redis: {settings.REDIS_URL}")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise


async def disconnect_redis():
    """断开 Redis 连接"""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Disconnected from Redis")


def get_mongodb():
    """获取 MongoDB 数据库实例"""
    if mongodb_db is None:
        raise RuntimeError("MongoDB not connected")
    return mongodb_db


def get_redis():
    """获取 Redis 客户端实例"""
    if redis_client is None:
        raise RuntimeError("Redis not connected")
    return redis_client

