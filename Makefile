.PHONY: help build run stop logs clean dev test remote-build

# 默认目标
help:
	@echo "API2MCP - MCP Server 管理命令"
	@echo ""
	@echo "使用方法:"
	@echo "  make build        - 本地构建 Docker 镜像"
	@echo "  make run          - 启动服务（后台运行）"
	@echo "  make stop         - 停止服务"
	@echo "  make logs         - 查看日志"
	@echo "  make clean        - 清理 Docker 资源"
	@echo "  make dev          - 本地开发模式运行"
	@echo "  make test         - 运行测试"
	@echo "  make remote-build - 远程服务器构建并下载镜像"
	@echo ""

# 构建 Docker 镜像
build:
	docker-compose -f docker/docker-compose.yml build

# 启动服务
run:
	docker-compose -f docker/docker-compose.yml up -d

# 停止服务
stop:
	docker-compose -f docker/docker-compose.yml down

# 查看日志
logs:
	docker-compose -f docker/docker-compose.yml logs -f

# 清理 Docker 资源
clean:
	docker-compose -f docker/docker-compose.yml down -v --rmi local
	docker system prune -f

# 本地开发模式
dev:
	python -m src.api.main

# 运行测试
test:
	python playground/test_mcp_simple.py
	python playground/test_mcp_client.py

# 安装依赖
install:
	pip install -r requirements.txt

# 重启服务
restart: stop run

# 远程服务器构建
remote-build:
	@bash docker/remote_build.sh

