"""日志配置模块 - 使用 loguru"""
import sys
from loguru import logger

# 移除默认处理器
logger.remove()

# 添加控制台输出
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
)

# 添加文件输出
logger.add(
    "src/logs/mcp_server_{time:YYYY-MM-DD}.log",
    rotation="00:00",  # 每天轮转
    retention="7 days",  # 保留7天
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    enqueue=True,
)

__all__ = ["logger"]

