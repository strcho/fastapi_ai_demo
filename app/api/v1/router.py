"""API v1 路由聚合"""
from fastapi import APIRouter

from app.api.v1.endpoints import items
from app.core.config import settings

api_router = APIRouter()

# 注册各个端点路由
api_router.include_router(
    items.router,
    prefix="/items",
    tags=["items"]
)

