.PHONY: help install install-dev run test lint format clean docker-build docker-up docker-down

help:
	@echo "可用的命令:"
	@echo "  make install       - 安装生产依赖"
	@echo "  make install-dev   - 安装开发依赖"
	@echo "  make run           - 运行应用"
	@echo "  make test          - 运行测试"
	@echo "  make lint          - 代码检查"
	@echo "  make format        - 代码格式化"
	@echo "  make clean         - 清理缓存文件"
	@echo "  make docker-build  - 构建 Docker 镜像"
	@echo "  make docker-up     - 启动 Docker 容器"
	@echo "  make docker-down   - 停止 Docker 容器"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

lint:
	flake8 app/ tests/
	mypy app/

format:
	black app/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf logs

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

