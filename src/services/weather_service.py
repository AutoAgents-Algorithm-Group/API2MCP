"""天气数据处理服务"""
from collections import defaultdict
from typing import Any, Dict, List

from ..repository import PSR_TYPE_TO_DEVICE_TYPE, WEATHER_FAULT_RISKS
from .device_service import safe_to_int, normalize_psr_type


def process_weather_device_list(device_list: List[Dict[str, Any]] | None) -> List[Dict[str, Any]]:
    """处理天气设备列表，展平嵌套结构"""
    flattened: List[Dict[str, Any]] = []
    if not device_list:
        return flattened

    for device in device_list:
        if not isinstance(device, dict):
            continue
        flattened.append(device)
        for nested in device.get("riskDeviceList") or []:
            if isinstance(nested, dict):
                flattened.append(nested)

    return flattened


def generate_risk_statements(risk_devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """生成风险描述语句"""
    if not risk_devices:
        return []

    aggregation: Dict[str, set[str]] = defaultdict(set)

    for device in risk_devices:
        if not isinstance(device, dict):
            continue

        psr_type = normalize_psr_type(device.get("psrType"))
        device_type = PSR_TYPE_TO_DEVICE_TYPE.get(psr_type, "其他")
        risk_desc = device.get("riskDesc")

        if isinstance(risk_desc, str) and risk_desc.strip():
            aggregation[device_type].add(risk_desc.strip())

    results: List[Dict[str, Any]] = []
    for device_type in sorted(aggregation.keys()):
        results.append(
            {
                "device_type": device_type,
                "risk_descriptions": sorted(aggregation[device_type]),
            }
        )

    return results


def determine_risk_possibility_level(risk_ratio: float) -> str:
    """
    根据风险比例确定风险等级
    
    参数:
        risk_ratio: 风险设备数量与总沿线设备数量的比值
        
    返回:
        风险等级（"低"、"中"、"高"）
    """
    if risk_ratio < 0.1:
        return "低"
    if risk_ratio < 0.3:
        return "中"
    return "高"


def match_weather_fault_risks(weather_desc: Any) -> List[str]:
    """根据天气描述匹配故障风险"""
    if not isinstance(weather_desc, str):
        return []

    matched_risks: List[str] = []
    for keyword, risks in WEATHER_FAULT_RISKS.items():
        if keyword in weather_desc:
            matched_risks.extend(risks)

    # 去重并保持原有顺序
    seen: set[str] = set()
    deduped: List[str] = []
    for risk in matched_risks:
        if risk not in seen:
            deduped.append(risk)
            seen.add(risk)

    return deduped


def process_weather_data(weather_data: Dict[str, Any]) -> Dict[str, Any]:
    """处理天气数据并生成汇总信息"""
    if not isinstance(weather_data, dict):
        raise ValueError("weather_data 必须是字典。")

    device_fact_range = weather_data.get("deviceFactRange") or {}
    lightning_data = weather_data.get("lightningDetectionData") or []

    tower_devices = process_weather_device_list(weather_data.get("towerDeviceList"))
    station_devices = process_weather_device_list(weather_data.get("stationDeviceList"))
    risk_devices = tower_devices + station_devices

    total_devices = safe_to_int(weather_data.get("deviceNum"))
    risk_count = safe_to_int(weather_data.get("riskDeviceNum"))

    if total_devices == 0:
        return {
            "code": 9999,
            "success": False,
            "data": None,
            "msg": "无设备数据",
        }

    risk_ratio = risk_count / float(total_devices)

    data = {
        "weather_desc": weather_data.get("weather"),
        "temperature_range": device_fact_range.get("temperatureRange") or [],
        "rainfall_range": device_fact_range.get("rainfallRange") or [],
        "humidity_range": device_fact_range.get("humidityRange") or [],
        "wind_speed_range": device_fact_range.get("windSpeedRange") or [],
        "lightning_strike_count": len(lightning_data),
        "risk_device_percentage": risk_ratio,
        "risk_possibility_level": determine_risk_possibility_level(risk_ratio),
        "risk_statements_by_type": generate_risk_statements(risk_devices),
        "weather_fault_risks": match_weather_fault_risks(weather_data.get("weather")),
    }

    return {
        "code": 10000,
        "success": True,
        "data": data,
        "msg": "操作成功",
    }


__all__ = [
    "process_weather_device_list",
    "generate_risk_statements",
    "determine_risk_possibility_level",
    "match_weather_fault_risks",
    "process_weather_data",
]

