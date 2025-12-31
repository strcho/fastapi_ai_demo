"""Items API 测试"""
import pytest


@pytest.mark.asyncio
async def test_root(client):
    """测试根路径"""
    response = await client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_health_check(client):
    """测试健康检查"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_item(client):
    """测试创建物品"""
    item_data = {
        "name": "测试物品",
        "description": "这是一个测试物品",
        "price": 99.99
    }
    response = await client.post("/api/v1/items/", json=item_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["price"] == item_data["price"]
    assert "id" in data
    assert "created_at" in data
    return data["id"]


@pytest.mark.asyncio
async def test_get_item(client):
    """测试获取物品"""
    # 先创建一个物品
    item_id = await test_create_item(client)
    
    # 获取物品
    response = await client.get(f"/api/v1/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == "测试物品"


@pytest.mark.asyncio
async def test_get_items(client):
    """测试获取所有物品"""
    # 先创建一些物品
    await test_create_item(client)
    await test_create_item(client)
    
    response = await client.get("/api/v1/items/")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) >= 2


@pytest.mark.asyncio
async def test_update_item(client):
    """测试更新物品"""
    # 先创建一个物品
    item_id = await test_create_item(client)
    
    # 更新物品
    update_data = {
        "name": "更新后的物品",
        "price": 199.99
    }
    response = await client.put(f"/api/v1/items/{item_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["price"] == update_data["price"]
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_delete_item(client):
    """测试删除物品"""
    # 先创建一个物品
    item_id = await test_create_item(client)
    
    # 删除物品
    response = await client.delete(f"/api/v1/items/{item_id}")
    assert response.status_code == 204
    
    # 验证物品已删除
    response = await client.get(f"/api/v1/items/{item_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_item(client):
    """测试获取不存在的物品"""
    response = await client.get("/api/v1/items/99999")
    assert response.status_code == 404

