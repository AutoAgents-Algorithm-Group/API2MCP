"""配置模块 - 硬编码默认值"""
from typing import Dict

from pydantic import BaseModel, computed_field


class DataServiceConfig(BaseModel):
    """数据服务配置"""
    
    model_config = {"frozen": True}
    
    base_url: str = "http://25.91.83.60:18081"
    timeout: float = 10.0
    outage_token: str = "7xK#9Pm!2LqW5sR@3vY6nZ$4dA8gH%1jU0oQ*9bV&cN"
    
    # 地貌服务配置
    landform_url: str = "http://192.168.11.145:38000"
    
    # MCP服务器配置
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 9090

    @computed_field
    @property
    def normalized_base_url(self) -> str:
        return self.base_url.rstrip("/")

    def build_headers(self) -> Dict[str, str]:
        if not self.outage_token:
            raise RuntimeError("未配置 Outage-Token。")
        return {"Outage-Token": self.outage_token}


# 全局配置实例
config = DataServiceConfig()

__all__ = ["config", "DataServiceConfig"]
