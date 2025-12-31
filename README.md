# FastAPI Best Practice

一个遵循最佳实践的 FastAPI 项目模板，集成了 MongoDB 和 Redis。

## 项目结构

```
fastapi-best-practice/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── endpoints/
│   │       │   ├── __init__.py
│   │       │   └── items.py    # 示例 API 路由（使用 MongoDB + Redis）
│   │       └── router.py       # 路由聚合
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # 配置管理（支持 .env）
│   │   ├── database.py         # MongoDB 和 Redis 连接管理
│   │   └── logging.py          # 日志配置
│   ├── models/
│   │   └── __init__.py
│   └── schemas/
│       ├── __init__.py
│       └── item.py             # Pydantic 模型
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # 测试配置和 fixtures
│   └── test_items.py           # API 测试
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .env                        # 不提交到 Git
├── Dockerfile
├── docker-compose.yml          # 包含 MongoDB 和 Redis 服务
├── docker-compose.prod.yml     # 生产环境 compose（可选）
├── Makefile
└── README.md
```

## 功能特性

- ✅ 清晰的项目结构
- ✅ 配置管理（支持 .env 文件）
- ✅ 日志系统
- ✅ API 版本控制
- ✅ Pydantic 数据验证
- ✅ CORS 支持
- ✅ **MongoDB 数据持久化存储**
- ✅ **Redis 缓存支持**
- ✅ **自动缓存失效机制**
- ✅ 完整的测试套件（异步测试）
- ✅ Docker 支持（包含 MongoDB 和 Redis）
- ✅ 开发工具（Makefile）

## 快速开始

### 1. 安装依赖

```bash
# 安装生产依赖
make install

# 或安装开发依赖（包含测试工具）
make install-dev
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并根据需要修改：

```bash
cp .env.example .env
```

环境变量配置说明：
- `MONGODB_URL`: MongoDB 连接地址（默认: `mongodb://localhost:27017`）
- `MONGODB_DB_NAME`: 数据库名称（默认: `fastapi_demo`）
- `REDIS_URL`: Redis 连接地址（默认: `redis://localhost:6379`）
- `REDIS_DB`: Redis 数据库编号（默认: `0`）
- `REDIS_CACHE_TTL`: 缓存过期时间（秒，默认: `3600`）

### 3. 启动数据库服务

**方式一：使用 Docker Compose（推荐）**

```bash
# 启动 MongoDB 和 Redis
docker-compose up -d mongodb redis

# 或使用 Makefile
make docker-up
```

**方式二：本地安装**

确保本地已安装并运行 MongoDB 和 Redis：
- MongoDB: https://www.mongodb.com/try/download/community
- Redis: https://redis.io/download

### 4. 运行应用

```bash
# 使用 Makefile
make run

# 或直接使用 uvicorn
uvicorn app.main:app --reload
```

应用将在 `http://localhost:8000` 启动。

### 5. 访问文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 使用 Docker

Docker Compose 配置包含了完整的服务栈：
- **web**: FastAPI 应用
- **mongodb**: MongoDB 数据库服务
- **redis**: Redis 缓存服务

### 开发环境

```bash
# 构建镜像
make docker-build

# 启动所有服务（包括 MongoDB 和 Redis）
make docker-up

# 停止所有服务
make docker-down

# 查看日志
docker-compose logs -f
```

### 生产环境

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 数据持久化

Docker Compose 配置了数据卷，确保数据持久化：
- MongoDB 数据存储在 `mongodb_data` 卷中
- Redis 数据存储在 `redis_data` 卷中

## 开发工具

### 运行测试

```bash
make test
```

### 代码格式化

```bash
make format
```

### 代码检查

```bash
make lint
```

### 清理缓存

```bash
make clean
```

## API 端点示例

### 获取所有物品

```bash
GET /api/v1/items/
```

### 获取单个物品

```bash
GET /api/v1/items/{item_id}
```

### 创建物品

```bash
POST /api/v1/items/
Content-Type: application/json

{
  "name": "测试物品",
  "description": "这是一个测试物品",
  "price": 99.99
}
```

### 更新物品

```bash
PUT /api/v1/items/{item_id}
Content-Type: application/json

{
  "name": "更新后的物品",
  "price": 199.99
}
```

### 删除物品

```bash
DELETE /api/v1/items/{item_id}
```

## 数据库说明

### MongoDB

- 用于数据持久化存储
- 使用 Motor（异步 MongoDB 驱动）
- 支持自动 ID 生成（使用计数器集合）
- 集合名称：`items`

### Redis

- 用于查询结果缓存
- 自动缓存失效机制：
  - GET 操作：先查缓存，未命中则查数据库并写入缓存
  - POST/PUT/DELETE 操作：更新数据库后自动清除相关缓存
- 缓存键格式：
  - 单个物品：`items:{item_id}`
  - 物品列表：`items:list:{skip}:{limit}`

## 技术栈

- **FastAPI**: 现代、快速的 Web 框架
- **Pydantic**: 数据验证和设置管理
- **Motor**: MongoDB 异步驱动
- **Redis**: 内存缓存数据库
- **Uvicorn**: ASGI 服务器
- **Pytest**: 测试框架（支持异步测试）
- **Docker**: 容器化部署
- **Docker Compose**: 多容器编排

## 测试

项目包含完整的测试套件，使用异步测试客户端：

```bash
# 运行所有测试
make test

# 运行特定测试
pytest tests/test_items.py -v
```

**注意**：运行测试前需要确保 MongoDB 和 Redis 服务正在运行。

## 许可证

MIT

