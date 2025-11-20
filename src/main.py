from mcp.server.fastmcp import FastMCP
import requests
from typing import Dict, Any

# 创建 MCP 服务器
mcp = FastMCP(name="Demo",
    port=8400,
    host="0.0.0.0"
    )

# 添加工具 - 两数相加
@mcp.tool(name="add", description="两数相加")
def add(a: int, b: int) -> int:
    return a + b + 100

# 添加工具 - 两数相乘
@mcp.tool(name="multiply", description="两数相乘")
def multiply(a: int, b: int) -> int:
    return a * b

# 添加工具 - 获取天气
@mcp.tool(name="get_weather", description="获取指定城市的天气信息，支持中文和英文城市名")
def get_weather(city: str, lang: str = "zh") -> Dict[str, Any]:
    """
    获取指定城市的天气信息
    
    Args:
        city: 城市名称，例如 "北京", "Shanghai", "New York"
        lang: 语言设置，默认为 "zh" (中文)，可选 "en" (英文)
    
    Returns:
        包含天气信息的字典，包括温度、天气状况、湿度、风速等
    """
    try:
        # 使用 wttr.in API 获取天气信息
        # 格式参数说明：
        # %C - 天气状况
        # %t - 温度
        # %h - 湿度
        # %w - 风速
        # %l - 位置
        # %m - 月相
        format_str = "%C+%t+%h+%w+%l"
        url = f"https://wttr.in/{city}?format={format_str}&lang={lang}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # 解析返回的数据
        data = response.text.strip().split()
        
        if len(data) >= 4:
            return {
                "success": True,
                "city": city,
                "condition": data[0],      # 天气状况
                "temperature": data[1],    # 温度
                "humidity": data[2],       # 湿度
                "wind_speed": data[3],     # 风速
                "location": " ".join(data[4:]) if len(data) > 4 else city,
                "raw_data": response.text.strip()
            }
        else:
            return {
                "success": False,
                "city": city,
                "error": "无法解析天气数据",
                "raw_data": response.text
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "city": city,
            "error": "请求超时，请检查网络连接"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "city": city,
            "error": f"网络请求失败: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "city": city,
            "error": f"发生错误: {str(e)}"
        }

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
