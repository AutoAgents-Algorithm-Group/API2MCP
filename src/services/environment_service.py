"""环境数据处理服务"""
from datetime import date
from typing import Any, Dict, Set

import requests

from ..utils import config, logger


def is_in_harvest_season(target_date: date) -> bool:
    """判断日期是否处于农业收割季（9月15日-10月31日）"""
    harvest_start = date(target_date.year, 9, 15)
    harvest_end = date(target_date.year, 10, 31)
    return harvest_start <= target_date <= harvest_end


def is_in_spring_and_summer_range(target_date: date) -> bool:
    """判断日期是否处于春夏季（4月1日-8月31日）"""
    spring_summer_start = date(target_date.year, 4, 1)
    spring_summer_end = date(target_date.year, 8, 31)
    return spring_summer_start <= target_date <= spring_summer_end


def get_work_address_info(item: dict) -> str:
    """获取市政施工地址信息"""
    construction_builder = []
    added_project_names: Set[str] = set()

    # 获取施工项目信息
    construction_project = item.get("constructionProject")
    if construction_project is None:
        construction_project = {}

    # 按优先级处理不同范围的项目：3公里 > 2公里 > 1公里
    three_km_projects = construction_project.get("threeKmProjects", [])
    two_km_projects = construction_project.get("twoKmProjects", [])
    one_km_projects = construction_project.get("oneKmProjects", [])

    # 处理3公里范围项目
    if three_km_projects and isinstance(three_km_projects, list):
        for project in three_km_projects:
            project_name = project.get("constructionName")
            if project_name and project_name not in added_project_names:
                added_project_names.add(project_name)
                address = project.get("address")
                if address:
                    construction_builder.append(address)

    # 处理2公里范围项目
    if two_km_projects and isinstance(two_km_projects, list):
        for project in two_km_projects:
            project_name = project.get("constructionName")
            if project_name and project_name not in added_project_names:
                added_project_names.add(project_name)
                address = project.get("address")
                if address:
                    construction_builder.append(address)

    # 处理1公里范围项目
    if one_km_projects and isinstance(one_km_projects, list):
        for project in one_km_projects:
            project_name = project.get("constructionName")
            if project_name and project_name not in added_project_names:
                added_project_names.add(project_name)
                address = project.get("address")
                if address:
                    construction_builder.append(address)

    return ",".join(construction_builder)


def get_landform(geo_position: str) -> str:
    """根据经纬度获取地貌信息"""
    try:
        # 分割经纬度
        split_pos = geo_position.split(",")
        if len(split_pos) < 2:
            return "经纬度格式错误"

        lon, lat = split_pos[0].strip(), split_pos[1].strip()
        url = f"{config.landform_url}/getDimao?lon={lon}&lat={lat}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        result_data = data.get("data", {}).get("stats", {}).get("classes")
        if not result_data:
            return "查询结果为空"

        if isinstance(result_data, dict):
            # 过滤掉None或空字符串的键
            valid_keys = [str(key) for key in result_data.keys() if key]
            if valid_keys:
                return ",".join(valid_keys)
            else:
                return "无有效水域类型"
        else:
            return "数据格式错误"
    except Exception as e:
        logger.error(f"调用地貌接口失败: {e}")
        return "未知"


def process_environment_data(environment: Dict[str, Any], outage_date: date) -> Dict[str, Any]:
    """处理环境信息"""
    if not isinstance(environment, dict):
        raise ValueError("environment 必须是字典。")

    environment_data = environment.get("data", [])

    # 处理地形和市政地址信息
    landform_list = []
    work_address_list = []
    for info in environment_data:
        landform = info.get("landform")
        if landform and "未知" not in landform and landform.strip():
            if landform not in landform_list:
                landform_list.append(landform)

        work_address = info.get("workAddress")
        if work_address and work_address not in work_address_list:
            work_address_list.append(work_address)

    # 构建最终结果
    result = {
        "是否处于农业收割季": '是' if is_in_harvest_season(outage_date) else '否',
        "是否处于春夏季": '是' if is_in_spring_and_summer_range(outage_date) else '否',
        "地貌": ', '.join(landform_list) if landform_list else '',
        "市政地址": ', '.join(work_address_list) if work_address_list else '',
        "无人机分析结果": "缺少数据",
    }

    return {
        "code": 10000,
        "success": True,
        "data": result,
        "msg": "操作成功"
    }


__all__ = [
    "is_in_harvest_season",
    "is_in_spring_and_summer_range",
    "get_work_address_info",
    "get_landform",
    "process_environment_data",
]

