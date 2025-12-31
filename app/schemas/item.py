"""Item 相关的 Pydantic 模式"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ItemBase(BaseModel):
    """Item 基础模式"""
    name: str = Field(..., description="物品名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="物品描述", max_length=500)
    price: float = Field(..., description="物品价格", gt=0)


class ItemCreate(ItemBase):
    """创建 Item 的模式"""
    pass


class ItemUpdate(BaseModel):
    """更新 Item 的模式"""
    name: Optional[str] = Field(None, description="物品名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="物品描述", max_length=500)
    price: Optional[float] = Field(None, description="物品价格", gt=0)


class ItemResponse(ItemBase):
    """Item 响应模式"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

