# FastAPI Best Practice

一个遵循最佳实践的 FastAPI 项目模板。

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
│   │       │   └── items.py    # 示例 API 路由
│   │       └── router.py       # 路由聚合
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # 配置管理（支持 .env）
│   │   └── logging.py          # 日志配置
│   ├── models/
│   │   └── __init__.py
│   └── schemas/
│       ├── __init__.py
│       └── item.py             # Pydantic 模型
├── tests/
│   ├── __init__.py
│   └── test_items.py
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .env                        # 不提交到 Git
├── Dockerfile
├── docker-compose.yml
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
- ✅ 完整的测试套件
- ✅ Docker 支持
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

### 3. 运行应用

```bash
# 使用 Makefile
make run

# 或直接使用 uvicorn
uvicorn app.main:app --reload
```

应用将在 `http://localhost:8000` 启动。

### 4. 访问文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 使用 Docker

### 开发环境

```bash
# 构建镜像
make docker-build

# 启动容器
make docker-up

# 停止容器
make docker-down
```

### 生产环境

```bash
docker-compose -f docker-compose.prod.yml up -d
```

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

## 技术栈

- **FastAPI**: 现代、快速的 Web 框架
- **Pydantic**: 数据验证和设置管理
- **Uvicorn**: ASGI 服务器
- **Pytest**: 测试框架
- **Docker**: 容器化部署

## 许可证

MIT

