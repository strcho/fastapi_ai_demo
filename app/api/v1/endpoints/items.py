"""Items API 端点"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
import json

from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse
from app.core.database import get_mongodb, get_redis
from app.core.config import settings

router = APIRouter()

# MongoDB 集合名称
ITEMS_COLLECTION = "items"


@router.get("/", response_model=List[ItemResponse], summary="获取所有物品")
async def get_items(skip: int = 0, limit: int = 100):
    """
    获取所有物品列表
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    """
    redis = get_redis()
    cache_key = f"items:list:{skip}:{limit}"
    
    # 尝试从 Redis 缓存获取
    cached_data = await redis.get(cache_key)
    if cached_data:
        items_data = json.loads(cached_data)
        # 转换 datetime 字符串回 datetime 对象
        result = []
        for item in items_data:
            item_copy = item.copy()
            item_copy["created_at"] = datetime.fromisoformat(item_copy["created_at"])
            if item_copy.get("updated_at"):
                item_copy["updated_at"] = datetime.fromisoformat(item_copy["updated_at"])
            result.append(ItemResponse(**item_copy))
        return result
    
    # 从 MongoDB 获取数据
    db = get_mongodb()
    cursor = db[ITEMS_COLLECTION].find().skip(skip).limit(limit).sort("created_at", -1)
    items = await cursor.to_list(length=limit)
    
    # 转换 ObjectId 为 int id
    items_data = []
    for item in items:
        item["id"] = item.pop("_id")
        # 转换 datetime 对象为字符串以便 JSON 序列化
        if "created_at" in item and isinstance(item["created_at"], datetime):
            item["created_at"] = item["created_at"].isoformat()
        if "updated_at" in item and item["updated_at"] and isinstance(item["updated_at"], datetime):
            item["updated_at"] = item["updated_at"].isoformat()
        items_data.append(item)
    
    # 缓存到 Redis
    await redis.setex(
        cache_key,
        settings.REDIS_CACHE_TTL,
        json.dumps(items_data, default=str)
    )
    
    # 转换回 datetime 对象用于响应模型
    result = []
    for item in items_data:
        item_copy = item.copy()
        item_copy["created_at"] = datetime.fromisoformat(item["created_at"])
        if item_copy.get("updated_at"):
            item_copy["updated_at"] = datetime.fromisoformat(item["updated_at"])
        result.append(ItemResponse(**item_copy))
    
    return result


@router.get("/{item_id}", response_model=ItemResponse, summary="获取单个物品")
async def get_item(item_id: int):
    """
    根据 ID 获取单个物品
    
    - **item_id**: 物品 ID
    """
    redis = get_redis()
    cache_key = f"items:{item_id}"
    
    # 尝试从 Redis 缓存获取
    cached_data = await redis.get(cache_key)
    if cached_data:
        item_data = json.loads(cached_data)
        item_data["created_at"] = datetime.fromisoformat(item_data["created_at"])
        if item_data.get("updated_at"):
            item_data["updated_at"] = datetime.fromisoformat(item_data["updated_at"])
        return ItemResponse(**item_data)
    
    # 从 MongoDB 获取数据
    db = get_mongodb()
    item = await db[ITEMS_COLLECTION].find_one({"_id": item_id})
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    # 转换 ObjectId 为 int id
    item["id"] = item.pop("_id")
    
    # 缓存到 Redis
    item_cache = item.copy()
    if isinstance(item_cache.get("created_at"), datetime):
        item_cache["created_at"] = item_cache["created_at"].isoformat()
    if item_cache.get("updated_at") and isinstance(item_cache["updated_at"], datetime):
        item_cache["updated_at"] = item_cache["updated_at"].isoformat()
    await redis.setex(
        cache_key,
        settings.REDIS_CACHE_TTL,
        json.dumps(item_cache, default=str)
    )
    
    return ItemResponse(**item)


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, summary="创建物品")
async def create_item(item: ItemCreate):
    """
    创建新物品
    
    - **name**: 物品名称（必填）
    - **description**: 物品描述（可选）
    - **price**: 物品价格（必填，必须大于0）
    """
    db = get_mongodb()
    redis = get_redis()
    
    # 获取下一个 ID（使用 MongoDB 的计数器集合）
    counter_collection = db["counters"]
    from pymongo import ReturnDocument
    counter = await counter_collection.find_one_and_update(
        {"_id": "item_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    item_id = counter.get("seq", 1) if counter else 1
    
    # 创建新物品
    now = datetime.now()
    new_item = {
        "_id": item_id,
        **item.model_dump(),
        "created_at": now,
        "updated_at": None
    }
    
    # 插入到 MongoDB
    await db[ITEMS_COLLECTION].insert_one(new_item)
    
    # 清除列表缓存
    async for key in redis.scan_iter(match="items:list:*"):
        await redis.delete(key)
    
    # 转换 ObjectId 为 id
    new_item["id"] = new_item.pop("_id")
    
    return ItemResponse(**new_item)


@router.put("/{item_id}", response_model=ItemResponse, summary="更新物品")
async def update_item(item_id: int, item_update: ItemUpdate):
    """
    更新物品信息
    
    - **item_id**: 物品 ID
    - **item_update**: 要更新的字段
    """
    db = get_mongodb()
    redis = get_redis()
    
    # 检查物品是否存在
    existing_item = await db[ITEMS_COLLECTION].find_one({"_id": item_id})
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    # 只更新提供的字段
    update_data = item_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    
    # 更新 MongoDB
    await db[ITEMS_COLLECTION].update_one(
        {"_id": item_id},
        {"$set": update_data}
    )
    
    # 清除相关缓存
    await redis.delete(f"items:{item_id}")
    async for key in redis.scan_iter(match="items:list:*"):
        await redis.delete(key)
    
    # 获取更新后的物品
    updated_item = await db[ITEMS_COLLECTION].find_one({"_id": item_id})
    updated_item["id"] = updated_item.pop("_id")
    
    return ItemResponse(**updated_item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除物品")
async def delete_item(item_id: int):
    """
    删除物品
    
    - **item_id**: 物品 ID
    """
    db = get_mongodb()
    redis = get_redis()
    
    # 检查物品是否存在
    result = await db[ITEMS_COLLECTION].delete_one({"_id": item_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    # 清除相关缓存
    await redis.delete(f"items:{item_id}")
    async for key in redis.scan_iter(match="items:list:*"):
        await redis.delete(key)
    
    return None

