"""MCP Server - 天气和工单 MCP 服务器"""
from datetime import date
from typing import Any, Dict, List

from fastmcp import FastMCP

from ..utils import config, logger
from ..services import (
    post_to_data_service,
    request_data_service,
    process_weather_data,
    process_device_info_data,
    process_environment_data,
    process_message_data,
    get_work_address_info,
    get_landform,
)

# 创建MCP服务器实例
mcp = FastMCP(
    "Weather and Work Order MCP Server",
    host=config.mcp_host,
    port=config.mcp_port
)


@mcp.tool(
    name="get_event_data",
    description="获取停电事件基本信息。",
)
def get_event_data(outage_number: str) -> Dict[str, Any]:
    """调用 `/outage/event/query` 接口获取停电事件信息。"""
    payload = {
        "outageNumber": outage_number
    }
    return post_to_data_service("/outage/event/query", payload)


@mcp.tool(
    name="get_weather_data",
    description="获取停电时间沿线天气分析数据，封装对天气数据服务的调用。",
)
def get_weather_data(outage_number: str, analysis_type: int) -> Dict[str, Any]:
    """调用 `/api/weather/data/portrait` 接口获取天气信息。"""
    if analysis_type not in (1, 2):
        raise ValueError("analysis_type 仅支持 1（事中分析）或 2（事后分析）。")

    payload = {
        "outageNumber": outage_number,
        "analysisType": analysis_type,
    }
    return post_to_data_service("/api/weather/data/portrait", payload)


@mcp.tool(
    name="work_order_query_tool",
    description="沿线诉求工单查询工具，获取沿线历史及当前客户工单信息。",
)
def work_order_query_tool(outage_number: str, analysis_type: int) -> Dict[str, Any]:
    """调用 `/appeal/appealListByOutageNumber` 接口获取沿线工单信息。"""
    if analysis_type not in (1, 2):
        raise ValueError("analysis_type 仅支持 1（事中分析）或 2（事后分析）。")

    payload = {
        "outageNumber": outage_number,
        "analysisType": analysis_type,
    }
    return post_to_data_service("/appeal/appealListByOutageNumber", payload)


@mcp.tool(
    name="weather_data_processing",
    description="处理并总结天气数据，获取天气数据后调用此工具处理天气数据并生成汇总天气信息",
)
def weather_data_processing(weather_data: Dict[str, Any]) -> Dict[str, Any]:
    """处理天气数据并生成汇总信息。"""
    return process_weather_data(weather_data)


@mcp.tool(
    name="environment_data_processing",
    description="处理总结环境信息",
)
def environment_data_processing(environment: Dict[str, Any], outage_date: date) -> Dict[str, Any]:
    """处理环境信息"""
    return process_environment_data(environment, outage_date)


@mcp.tool(
    name="get_drone_analysis",
    description="获取无人机图片分析结果",
)
def get_drone_analysis(outage_number: str, tower_ids: List[str]) -> Dict[str, Any]:
    """获取无人机图片分析结果"""
    payload = {
        "outageNumber": outage_number,
        "towerIds": tower_ids
    }
    return post_to_data_service("/api/drone/analysis", payload)


@mcp.tool(
    name="get_environment_raw_data",
    description="获取原始环境数据",
)
def get_environment_raw_data(outage_number: str) -> Dict[str, Any]:
    """获取原始环境数据"""
    payload = {
        "outageNumber": outage_number
    }

    # 调用接口获取原始数据
    raw_data = post_to_data_service("/outage-data/test/agent", payload)

    # 初始化infos变量
    infos = []

    # 如果请求成功且有数据
    if "data" in raw_data:
        infos = raw_data.get("data", [])

        # 确保infos是列表类型
        if isinstance(infos, list):
            for info in infos:
                if isinstance(info, dict):
                    # 获取地理位置
                    geo_position = info.get("geoPosition")
                    work_address = get_work_address_info(info)
                    landform = "未知"  # 默认值

                    if geo_position and isinstance(geo_position, str) and geo_position.strip():
                        # 调用地貌接口
                        landform = get_landform(geo_position.strip())

                        # 转换"不透水表面"为"建筑/城市道路"
                        if landform == "不透水表面":
                            landform = "建筑/城市道路"

                    # 添加地貌信息到数据中
                    info["landform"] = landform
                    info["workAddress"] = work_address

    # 返回处理后的数据
    return {
        "code": 10000,
        "success": True,
        "data": infos,
        "msg": "操作成功",
    }


@mcp.tool(
    name="get_message_data",
    description="获取保护报文数据，封装对保护报文数据服务的调用",
)
def get_message_data(outage_number: str, analysis_type: int) -> Dict[str, Any]:
    """调用 `/outage-data/outage/event/realMeasCenter/event/commonQuery/query` 接口获取保护报文信息。"""
    if analysis_type not in (1, 2):
        raise ValueError("analysis_type 仅支持 1（事中分析）或 2（事后分析）。")

    payload = {
        "outageNumber": outage_number,
        "analysisType": analysis_type,
    }
    return request_data_service(
        'POST',
        "/outage-data/outage/event/realMeasCenter/event/commonQuery/query",
        payload=payload
    )


@mcp.tool(
    name="get_wave_data",
    description="获取录波数据，封装对录播数据服务的调用",
)
def get_wave_data(outage_number: str, analysis_type: int) -> Dict[str, Any]:
    """调用 `/outage-data/outage/event/luboAnalyse` 接口获取录波信息。"""
    if analysis_type not in (1, 2):
        raise ValueError("analysis_type 仅支持 1（事中分析）或 2（事后分析）。")

    payload = {
        "outageNumber": outage_number,
        "analysisType": analysis_type,
    }
    return request_data_service('GET', "/outage-data/outage/event/luboAnalyse", params=payload)


@mcp.tool(
    name="message_data_processing",
    description="处理并总结报文、录波数据，生成报文智能体的输入数据",
)
def message_data_processing(res: str, wave_data_str: str) -> Dict[str, Any]:
    """处理报文和录波数据"""
    return process_message_data(res, wave_data_str)


@mcp.tool(
    name="get_device_info_data",
    description="获取设备信息数据，封装对设备数据服务的调用。",
)
def get_device_info_data(outage_number: str) -> Dict[str, Any]:
    """调用 `/outage-data/test/agent` 接口获取设备信息。

    参数:
        outage_number: 停电事件编号
    """
    payload = {
        "outageNumber": outage_number,
    }
    return post_to_data_service("/outage-data/test/agent", payload)


@mcp.tool(
    name="process_device_info_data",
    description="处理设备信息数据，生成大模型输入参数。",
)
def process_device_info(device_data: Dict[str, Any]) -> Dict[str, Any]:
    """处理设备信息数据并生成大模型输入参数。

    参数:
        device_data: 设备信息数据，由 get_device_info_data 工具获取
    """
    return process_device_info_data(device_data)


if __name__ == "__main__":
    logger.info(f"启动 MCP 服务器: {config.mcp_host}:{config.mcp_port}")
    mcp.run(transport="sse")
