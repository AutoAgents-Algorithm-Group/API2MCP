#!/bin/bash
# API2MCP - 远程服务器构建脚本
# 
# 在远程 Linux 服务器上构建 Docker 镜像，然后将构建好的镜像下载到本地
#
# 使用方法:
#   ./docker/remote_build.sh
#
# 环境变量:
#   BUILD_SERVER      - 服务器 IP (默认: 45.78.224.30)
#   BUILD_USER        - 服务器用户 (默认: root)
#   BUILD_PASS        - 服务器密码 (默认: autoagents@2023)
#   IMAGE_NAME        - 镜像名称 (默认: api2mcp-server:latest)

set -e

echo "=========================================="
echo "🚀 API2MCP - 远程服务器构建"
echo "=========================================="
echo ""

# ==================== 配置 ====================

SERVER_IP="${BUILD_SERVER:-45.78.224.30}"
SERVER_USER="${BUILD_USER:-root}"
SERVER_PASS="${BUILD_PASS:-autoagents@2023}"
REMOTE_BUILD_DIR="/opt/api2mcp-build"
LOCAL_OUTPUT_DIR="./dist"
IMAGE_NAME="${IMAGE_NAME:-api2mcp-server:latest}"
IMAGE_TAG=$(echo "$IMAGE_NAME" | tr ':' '-')

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "📋 构建配置:"
echo "   - 服务器: $SERVER_USER@$SERVER_IP"
echo "   - 远程目录: $REMOTE_BUILD_DIR"
echo "   - 镜像名称: $IMAGE_NAME"
echo "   - 本地输出: $LOCAL_OUTPUT_DIR"
echo ""

# ==================== 工具函数 ====================

# 检查 sshpass
check_sshpass() {
    if ! command -v sshpass &> /dev/null; then
        echo "⚠️  sshpass 未安装，正在安装..."
        if [[ "$(uname -s)" == "Darwin" ]]; then
            # macOS
            if command -v brew &> /dev/null; then
                brew install hudochenkov/sshpass/sshpass
            else
                echo "❌ 请先安装 Homebrew 或手动安装 sshpass"
                exit 1
            fi
        elif command -v apt-get &> /dev/null; then
            # Debian/Ubuntu
            sudo apt-get update && sudo apt-get install -y sshpass
        elif command -v yum &> /dev/null; then
            # CentOS/RHEL
            sudo yum install -y sshpass
        else
            echo "❌ 无法自动安装 sshpass，请手动安装"
            exit 1
        fi
    fi
    echo "✓ sshpass: 已安装"
}

# SSH 命令封装
ssh_cmd() {
    sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$SERVER_USER@$SERVER_IP" "$@"
}

# SCP 命令封装
scp_cmd() {
    sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no "$@"
}

# ==================== 步骤 1: 检查依赖 ====================

echo "🔍 步骤 1/5: 检查本地和远程依赖..."
echo ""

check_sshpass

# 检查 rsync
if ! command -v rsync &> /dev/null; then
    echo "❌ rsync 未安装，请先安装 rsync"
    exit 1
fi
echo "✓ rsync: 已安装"

# 测试 SSH 连接
echo "测试 SSH 连接..."
if ! ssh_cmd "echo 'SSH 连接成功'"; then
    echo "❌ SSH 连接失败，请检查服务器配置"
    exit 1
fi
echo ""

# ==================== 步骤 2: 准备远程环境 ====================

echo "🔧 步骤 2/5: 准备远程环境..."
echo ""

ssh_cmd "mkdir -p $REMOTE_BUILD_DIR"

# 检查 Docker
if ! ssh_cmd "docker info > /dev/null 2>&1"; then
    echo "❌ Docker 未运行或未安装"
    exit 1
fi
echo "✓ Docker: 已就绪"

# 清理旧的构建目录
ssh_cmd "rm -rf $REMOTE_BUILD_DIR/project && mkdir -p $REMOTE_BUILD_DIR/project"

echo "✓ 远程环境准备完成"
echo ""

# ==================== 步骤 3: 同步代码 ====================

echo "📤 步骤 3/5: 同步代码到服务器..."
echo ""

cd "$PROJECT_ROOT"

# 使用 rsync 同步代码，排除不必要的文件
rsync -avz --progress \
    -e "sshpass -p '$SERVER_PASS' ssh -o StrictHostKeyChecking=no" \
    --exclude 'node_modules' \
    --exclude '__pycache__' \
    --exclude '.git' \
    --exclude 'dist' \
    --exclude 'logs' \
    --exclude 'venv' \
    --exclude '.venv' \
    --exclude '*.log' \
    --exclude '*.pyc' \
    --exclude '.pytest_cache' \
    --exclude '.mypy_cache' \
    --exclude '.DS_Store' \
    --exclude 'playground' \
    ./ "$SERVER_USER@$SERVER_IP:$REMOTE_BUILD_DIR/project/"

echo ""
echo "✓ 代码同步完成"
echo ""

# ==================== 步骤 4: 远程构建 ====================

echo "🏗️  步骤 4/5: 在服务器上构建 Docker 镜像..."
echo ""

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="${IMAGE_TAG}-${TIMESTAMP}.tar.gz"

ssh_cmd "cd $REMOTE_BUILD_DIR/project && \
    echo '开始构建 Docker 镜像...' && \
    echo '' && \
    DOCKER_BUILDKIT=0 docker build \
        --platform linux/amd64 \
        -f docker/Dockerfile \
        -t $IMAGE_NAME \
        . && \
    echo '' && \
    echo '导出镜像...' && \
    mkdir -p dist && \
    docker save $IMAGE_NAME | gzip > dist/$ARCHIVE_NAME && \
    echo '' && \
    echo '✓ 镜像构建并导出完成'"

echo ""
echo "✓ 远程构建完成"
echo ""

# ==================== 步骤 5: 下载镜像 ====================

echo "📥 步骤 5/5: 下载构建产物..."
echo ""

# 获取最新的镜像文件
REMOTE_IMAGE="$REMOTE_BUILD_DIR/project/dist/$ARCHIVE_NAME"

# 检查远程文件是否存在
if ! ssh_cmd "test -f $REMOTE_IMAGE"; then
    echo "❌ 未找到构建产物: $REMOTE_IMAGE"
    exit 1
fi

echo "下载: $REMOTE_IMAGE"

# 创建本地输出目录
mkdir -p "$LOCAL_OUTPUT_DIR"

# 下载镜像
scp_cmd "$SERVER_USER@$SERVER_IP:$REMOTE_IMAGE" "$LOCAL_OUTPUT_DIR/"

# 获取本地文件信息
LOCAL_IMAGE="$LOCAL_OUTPUT_DIR/$ARCHIVE_NAME"
FILE_SIZE=$(du -h "$LOCAL_IMAGE" | cut -f1)

echo ""
echo "✓ 下载完成"
echo ""

# ==================== 清理远程环境（可选）====================

echo "🧹 清理远程构建目录..."
ssh_cmd "rm -rf $REMOTE_BUILD_DIR/project"
echo "✓ 清理完成"
echo ""

# ==================== 完成 ====================

echo "=========================================="
echo "🎉 远程构建完成！"
echo "=========================================="
echo ""
echo "📊 构建信息:"
echo "   文件: $LOCAL_IMAGE"
echo "   大小: $FILE_SIZE"
echo "   镜像: $IMAGE_NAME"
echo ""
echo "📦 加载镜像到本地 Docker:"
echo "   gunzip -c $LOCAL_IMAGE | docker load"
echo ""
echo "🚀 运行容器:"
echo "   docker run -d \\"
echo "     -p 9090:9090 \\"
echo "     --restart unless-stopped \\"
echo "     --name api2mcp-server \\"
echo "     $IMAGE_NAME"
echo ""
echo "🔗 访问 SSE 端点:"
echo "   http://localhost:9090/sse"
echo ""

