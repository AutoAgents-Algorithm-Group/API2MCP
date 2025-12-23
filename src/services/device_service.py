"""设备数据处理服务"""
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Set

from ..repository import (
    PSR_TYPE_TO_DEVICE_TYPE,
    DEVICE_AFFILIATED_MAP,
    DEVICE_AFFILIATED_FIELD_MAP,
    CONDUCTOR_CODE,
    CONDUCTOR_CODES,
    CABLE_CODE,
    TOWER_CODE,
    HARDWARE_CODE,
    HARDWARE_CODES,
    SWITCH_CODE,
    SWITCH_CODES,
    TRANSFORMER_CODE,
    BILEIQI_CODE,
    STATION_CODE,
)
from ..utils import logger


def safe_to_int(value: Any, default: int = 0) -> int:
    """将值安全转换为整数"""
    if value is None:
        return default
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except (ValueError, TypeError):
        return default


def normalize_psr_type(value: Any) -> str:
    """标准化PSR类型"""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip().lower()
    return str(value).strip().lower()


def get_affiliated_psr_id(data: List[Dict[str, Any]], item: Dict[str, Any], device_psr_type: str) -> str:
    """
    获取所属设备ID
    
    Args:
        data: 所有设备数据列表
        item: 当前设备数据
        device_psr_type: 设备PSR类型
        
    Returns:
        所属设备ID
    """
    psr_type = item.get("psr_type", "")

    # 电缆终端和电缆接头需要找到起点位置为终端或接头的电缆段id作为所属设备id
    if psr_type in ["0202", "0203"]:
        psr_id = item.get("psr_id", "")
        for segment in data:
            if segment.get("psr_type") == "0201":
                start_position = segment.get("start_position", "")
                end_position = segment.get("end_position", "")
                if start_position == psr_id or end_position == psr_id:
                    return segment.get("psr_id", "")
        return ""

    # 其他设备类型根据字段映射获取所属设备ID
    field = DEVICE_AFFILIATED_FIELD_MAP.get(device_psr_type)
    if field:
        return item.get(field, "")

    return ""


def calculate_device_risk(device: Dict[str, Any]) -> tuple[str, float, str, int]:
    """计算设备风险等级"""
    if not isinstance(device, dict):
        return "未知风险", 0.0, "未知", 0

    try:
        # 设备类型常量
        TOWER_TYPE = "0103"  # 杆塔
        INSULATOR_TYPE = "0103001"  # 绝缘子
        HARDWARE_TYPE = "0103002"  # 金具
        GUY_WIRE_TYPE = "0103005"  # 拉线

        # 获取设备类型
        device_type = device.get("device_type", "")
        affiliated_psr_type = device.get("affiliated_psr_type", "")

        # 获取启动运行时间
        start_run_time = device.get("start_time", "")
        if device_type in ["0103002", "0103001", "0306"]:
            start_run_time = device.get("operate_date", "")

        # 如果没有启动运行时间，设置为未知风险
        if not start_run_time:
            return "未知风险", 0.0, "未知", 0

        sdf = datetime.strptime(start_run_time, "%Y-%m-%d %H:%M:%S")
        current_date = datetime.now()

        # 计算运行时间（年）
        run_time_days = (current_date - sdf).days
        run_time_years = run_time_days / 365.0
        formatted_run_time_years = round(run_time_years, 1)

        # 处理缺陷列表（根据设备类型过滤）
        defect_list = device.get("defect_list", [])
        fault_list = device.get("fault_list", [])
        hidden_list = device.get("hidden_list", [])
        parent_defect_list = device.get("parent_defect_list", [])

        processed_defect_list = []

        if device_type == TOWER_TYPE:
            # 杆塔：只保留与杆塔或通道相关的缺陷
            for defect in parent_defect_list + defect_list:
                if isinstance(defect, dict):
                    eliminated_state = defect.get("eliminatedState", "")
                    component_type = defect.get("componentTypeName", "")
                    if eliminated_state == "0" and ("杆塔" in component_type or "通道" in component_type):
                        processed_defect_list.append(defect)

        elif device_type in CONDUCTOR_CODES:
            # 导线：添加与导线相关的缺陷（来自父节点）
            for defect in parent_defect_list:
                if isinstance(defect, dict):
                    eliminated_state = defect.get("eliminatedState", "")
                    component_type = defect.get("componentTypeName", "")
                    if eliminated_state == "0" and "导线" in component_type:
                        processed_defect_list.append(defect)

            # 添加设备自身的缺陷
            processed_defect_list.extend([d for d in defect_list if isinstance(d, dict)])

        elif device_type in HARDWARE_CODES:
            # 金具：根据子类型处理
            for defect in parent_defect_list:
                if isinstance(defect, dict):
                    eliminated_state = defect.get("eliminatedState", "")
                    component_type = defect.get("componentTypeName", "")

                    if eliminated_state == "0":
                        if device_type == INSULATOR_TYPE and "绝缘子" in component_type:
                            processed_defect_list.append(defect)
                        elif device_type == HARDWARE_TYPE and "金具" in component_type:
                            processed_defect_list.append(defect)
                        elif device_type == GUY_WIRE_TYPE and "拉线" in component_type:
                            processed_defect_list.append(defect)

            # 添加设备自身的缺陷
            processed_defect_list.extend([d for d in defect_list if isinstance(d, dict)])

        elif device_type in SWITCH_CODES and affiliated_psr_type == TOWER_TYPE:
            # 杆塔上的开关：添加与开关相关的缺陷（来自父节点）
            for defect in parent_defect_list:
                if isinstance(defect, dict):
                    eliminated_state = defect.get("eliminatedState", "")
                    component_type = defect.get("componentTypeName", "")
                    if eliminated_state == "0" and "开关" in component_type:
                        processed_defect_list.append(defect)

            # 添加设备自身的缺陷
            processed_defect_list.extend([d for d in defect_list if isinstance(d, dict)])

        else:
            # 其他设备：使用自身的缺陷列表
            processed_defect_list = [d for d in defect_list if isinstance(d, dict)]

        # 更新设备的缺陷列表为处理后的列表
        device["processed_defect_list"] = processed_defect_list

        # 检查是否存在风险
        has_risk = False

        # 检查故障列表
        if not has_risk and isinstance(fault_list, list):
            for fault in fault_list:
                if isinstance(fault, dict):
                    fault_status = fault.get("faultStatus", "")
                    if fault_status in ["01", "02"]:  # 01: 未处理, 02: 处理中
                        has_risk = True
                        break

        # 检查缺陷列表（使用处理后的缺陷列表）
        if not has_risk:
            for defect in processed_defect_list:
                if isinstance(defect, dict):
                    eliminated_state = defect.get("eliminatedState", "")
                    if eliminated_state == "0":  # 0: 未消除
                        if device_type == TOWER_TYPE:
                            component_type = defect.get("componentTypeName", "")
                            if "杆塔" in component_type:
                                has_risk = True
                                break
                            continue
                        has_risk = True
                        break

        # 检查隐患列表
        if not has_risk and isinstance(hidden_list, list):
            for hidden in hidden_list:
                if isinstance(hidden, dict):
                    state = hidden.get("state", "")
                    if state in ["16", "09"]:  # 16: 未整改, 09: 整改中
                        has_risk = True
                        break

        # 检查历史记录
        if not has_risk:
            # 检查任何类型的历史记录
            history_lists = [
                device.get("defect_history_list", []),
                device.get("hidden_history_list", []),
                device.get("fault_history_list", [])
            ]

            for history_list in history_lists:
                if isinstance(history_list, list) and len(history_list) > 0:
                    has_risk = True
                    break

        # 检查家族缺陷
        if not has_risk:
            has_family_defect = device.get("has_family_defect", False)
            if has_family_defect:
                has_risk = True

        # 计算设备得分
        fault_score = 35
        defect_score = 30
        hazard_score = 25
        patrol_score = 10

        fault_score = max(fault_score - safe_to_int(device.get("fault", 0)) * 5, 0)
        defect_score = max(defect_score - safe_to_int(device.get("defect", 0)) * 3, 0)
        hazard_score = max(hazard_score - safe_to_int(device.get("hazard", 0)) * 2, 0)

        long_years = "否"
        total_score = fault_score + defect_score + hazard_score + patrol_score

        return ("是" if has_risk else "否"), formatted_run_time_years, long_years, total_score

    except ValueError as e:
        logger.error(f"解析设备运行时间失败: {e}")
        return "未知风险", 0.0, "未知", 0
    except Exception as e:
        logger.error(f"计算设备风险失败: {e}")
        return "未知风险", 0.0, "未知", 0


def build_tree_structure(device_info_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """构建设备树形结构"""
    # 创建设备映射
    device_map = {device["psr_id"]: device for device in device_info_list}
    root_devices: List[Dict[str, Any]] = []

    # 标记根节点（没有父节点的设备或特定类型的设备）
    root_types = {"0103", "0338", "0337"}  # 杆塔、站房、电缆段等

    for device in device_info_list:
        device_type = device["device_type"]
        affiliated_psr_id = device["affiliated_psr_id"]

        if not affiliated_psr_id or device_type in root_types:
            # 添加子节点列表
            device["children"] = []
            root_devices.append(device)
        else:
            # 添加到父节点的子节点列表
            parent = device_map.get(affiliated_psr_id)
            if parent:
                if "children" not in parent:
                    parent["children"] = []
                parent["children"].append(device)

    return root_devices


def process_device_list(device_list: Any) -> List[Dict[str, Any]]:
    """处理设备列表，转换为统一格式"""
    if not isinstance(device_list, list):
        return []

    processed = []
    for device in device_list:
        if not isinstance(device, dict):
            continue

        processed.append({
            "name": device.get("name", ""),
            "psr_id": device.get("psr_id", ""),
            "psrType": device.get("psrType", ""),
        })

    return processed


def get_device_category(device_type_code: str) -> str:
    """根据设备类型代码获取设备类别"""
    if device_type_code in CONDUCTOR_CODE:
        return "导线"
    elif device_type_code in CABLE_CODE:
        return "电缆"
    elif device_type_code in TOWER_CODE:
        return "杆塔"
    elif device_type_code in HARDWARE_CODE:
        return "金具"
    elif device_type_code in SWITCH_CODE:
        return "开关"
    elif device_type_code in TRANSFORMER_CODE:
        return "配变"
    elif device_type_code in BILEIQI_CODE:
        return "避雷器"
    elif device_type_code in STATION_CODE:
        return "站房"
    else:
        return "其他"


def process_device_info_data(device_data: Dict[str, Any]) -> Dict[str, Any]:
    """处理设备信息数据并生成大模型输入参数"""
    if not isinstance(device_data, dict):
        raise ValueError("device_data 必须是字典。")

    # 检查设备数据是否成功获取
    if not device_data.get("success", False):
        error_msg = device_data.get("msg", "设备数据获取失败")
        return {
            "code": 9999,
            "success": False,
            "data": None,
            "msg": error_msg,
        }

    data = device_data.get("data", [])
    if not isinstance(data, list):
        return {
            "code": 9999,
            "success": False,
            "data": None,
            "msg": "设备数据格式错误",
        }

    # 1. 数据去重
    seen_psr_ids: Set[str] = set()
    unique_devices = []
    for device in data:
        if not isinstance(device, dict):
            continue

        psr_id = device.get("psr_id", "")
        if psr_id and psr_id not in seen_psr_ids:
            seen_psr_ids.add(psr_id)
            unique_devices.append(device)

    if not unique_devices:
        return {
            "code": 9999,
            "success": False,
            "data": None,
            "msg": "无有效设备数据",
        }

    # 2. 构建设备基本信息
    device_info_list = []
    for device in unique_devices:
        device_type = normalize_psr_type(device.get("psrType"))

        # 电缆类型设备暂时不处理
        if device_type == "xndl":
            continue

        device_info = {
            "device_name": device.get("name", "未知设备"),
            "psr_id": device.get("psr_id", ""),
            "device_type": device_type,
            "device_type_name": PSR_TYPE_TO_DEVICE_TYPE.get(device_type, "其他"),
            "line_name": device.get("line_and_name", ""),
            "fault_count": safe_to_int(device.get("fault")),
            "defect_count": safe_to_int(device.get("defect")),
            "hidden_count": safe_to_int(device.get("hazard")),
            "inspection_count": safe_to_int(device.get("patrol")),
            "run_year": device.get("equipRunYear", ""),
            "geo_position": device.get("geo_positon", ""),
            "affiliated_psr_id": get_affiliated_psr_id(unique_devices, device, device_type),
            "affiliated_psr_type": DEVICE_AFFILIATED_MAP.get(device_type),
            # 负面清单列表
            "fault_list": device.get("faultList", []),
            "defect_list": device.get("defectList", []),
            "hidden_list": device.get("hazardList", []),
            "inspection_list": device.get("patrolList", []),
            "defect_history_list": device.get("defectHistoryList", []),
            "inspection_history_list": device.get("patrolHistoryList", []),
            "fault_history_list": device.get("faultHistoryList", []),
            "hidden_history_list": device.get("hazardHistoryList", []),
            # 历史记录数量
            "fault_history_count": len(device.get("faultHistoryList", [])),
            "defect_history_count": len(device.get("defectHistoryList", [])),
            "hidden_history_count": len(device.get("hazardHistoryList", [])),
            "inspection_history_count": len(device.get("patrolHistoryList", [])),
            "rated_current_data": device.get("ratedState", ""),
            # 家族缺陷相关字段
            "has_family_defect": any([
                device.get("hasFamilyHazard", False),
                device.get("hasFamilyDefect", False),
                device.get("hasFamilyFault", False)
            ]),
            "family_hazard_count": safe_to_int(device.get("familyHazardCount")),
            "family_fault_count": safe_to_int(device.get("familyFaultCount")),
            "family_defect_count": safe_to_int(device.get("familyDefectCount")),
            # 其他字段
            "line_type": device.get("lineType", ""),
            "wire_type": device.get("wireType", ""),
            "span": device.get("span", 0.0),
            # 设备投运时间
            "run_time": device.get("start_time", "") if device_type not in ["0103002", "0103001", "0306"] else device.get("operate_date", "")
        }
        device_info_list.append(device_info)

    # 3. 计算设备风险
    risk_devices = set()
    for device in device_info_list:
        risk_level, run_time_years, long_years, device_score = calculate_device_risk(device)
        device["risk_level"] = risk_level
        device["run_time_years"] = run_time_years
        device["long_years"] = long_years
        device["device_score"] = device_score
        if risk_level == "是":
            risk_devices.add(device["psr_id"])

    # 4. 构建树形结构
    tree_structure = build_tree_structure(device_info_list)

    # 5. 统计设备类型
    device_type_stats = defaultdict(lambda: {"total": 0, "risk": 0})
    for device in device_info_list:
        type_name = device["device_type_name"]
        device_type_stats[type_name]["total"] += 1
        if device["psr_id"] in risk_devices:
            device_type_stats[type_name]["risk"] += 1

    # 转换为列表格式
    type_stats_list = []
    for type_name, stats in device_type_stats.items():
        type_stats_list.append({
            "device_type": type_name,
            "total_count": stats["total"],
            "risk_count": stats["risk"],
            "risk_ratio": stats["risk"] / stats["total"] if stats["total"] > 0 else 0,
        })

    # 6. 获取设备类型分布
    device_type_distribution = defaultdict(int)
    for device in device_info_list:
        device_type_distribution[device["device_type_name"]] += 1

    # 按设备类别分组
    devices_by_category = defaultdict(list)
    for device in device_info_list:
        category = get_device_category(device.get("device_type", ""))
        devices_by_category[category].append(device)

    # 设备类型统计数组
    device_type_stats_array = []
    unique_contents = set()

    for category, devices in devices_by_category.items():
        type_stat = {
            "设备类型": category,
            "总数": len(devices),
            "风险数": 0,
            "近90天内故障数量": 0,
            "近90天内缺陷数量": 0,
            "近90天内隐患数量": 0,
            "历史故障数量": 0,
            "历史缺陷数量": 0,
            "历史隐患数量": 0,
            "家族性缺陷数量": 0,
            "家族性隐患数量": 0,
            "家族性故障数量": 0,
        }

        # 统计各类数量
        for device in devices:
            # 风险数量
            if device.get("risk_level") == "是":
                type_stat["风险数"] += 1

            # 近90天统计
            type_stat["近90天内故障数量"] += device.get("fault_count", 0)
            type_stat["近90天内缺陷数量"] += device.get("defect_count", 0)
            type_stat["近90天内隐患数量"] += device.get("hidden_count", 0)

            # 历史统计
            type_stat["历史故障数量"] += device.get("fault_history_count", 0)
            type_stat["历史缺陷数量"] += device.get("defect_history_count", 0)
            type_stat["历史隐患数量"] += device.get("hidden_history_count", 0)

            # 家族性统计
            type_stat["家族性缺陷数量"] += device.get("family_defect_count", 0)
            type_stat["家族性隐患数量"] += device.get("family_hazard_count", 0)
            type_stat["家族性故障数量"] += device.get("family_fault_count", 0)

        # 计算风险比例
        type_stat["风险比例"] = type_stat["风险数"] / type_stat["总数"] if type_stat["总数"] > 0 else 0

        # 故障、缺陷、隐患总结
        type_stat["故障总结"] = "该类型设备可能存在故障"
        type_stat["缺陷总结"] = "该类型设备可能存在缺陷"
        type_stat["隐患总结"] = "该类型设备可能存在隐患"

        device_type_stats_array.append(type_stat)

    # 设备类型统计
    device_type_stats_new = []
    for stat in device_type_stats_array:
        device_type_stats_new.append({
            "设备类型": stat["设备类型"],
            "总数": stat["总数"],
            "风险数": stat["风险数"],
            "风险比例": stat["风险比例"],
        })

    # 线路导线类型统计
    line_type = "无数据来源"
    wire_type = "无数据来源"
    line_name = ""
    max_span = 0.0
    tower_des = ""

    # 一次性遍历获取所有需要的信息
    for device in device_info_list:
        # 获取最大档距
        device_span = device.get("span", 0.0)
        if device_span > max_span:
            max_span = device_span

        # 获取线路名称
        if not line_name and device.get("line_name"):
            line_name = device["line_name"]

        # 获取线路类型和导线类型
        if (line_type == "无数据来源" or wire_type == "无数据来源") and \
                device.get("line_type") and device.get("wire_type"):
            line_type = device["line_type"]
            wire_type = device["wire_type"]

    if max_span > 100:
        tower_des = f",且线路上杆塔存在档距过大(最大档距为 {max_span} 米)"

    # 构建线路导线描述
    line_wire_des = ""
    if wire_type == "其他":
        line_wire_des = f"{line_name}为{line_type}线路{tower_des}."
    else:
        line_wire_des = f"{line_name}为{line_type}线路, 导线类型为{wire_type}{tower_des}."

    # 重过载统计
    rated_date = ""
    for device in device_info_list:
        if device.get("rated_current_data"):
            rated_date = device["rated_current_data"]
            break

    overloaded = rated_date in {"重载", "过载"}

    # 风险设备数描述
    risk_devices_desc = f"根据设备近期及历史同期的隐患、缺陷、故障、巡视记录、设备家族性缺陷推断该线路上目前有{len(risk_devices)}个设备存在风险；"

    # 设备风险描述
    device_risk_desc = []
    unique_descriptions = set()

    for device in device_info_list:
        if device.get("risk_level") != "是":
            continue

        # 构建设备风险描述
        risk_desc = []
        if device.get("run_time"):
            risk_desc.append(f"该设备于{device['run_time']}投运。")

        # 近90天数据
        recent_data = []
        if device.get("fault_count") > 0:
            recent_data.append("存在故障未处理")
        if device.get("defect_count") > 0:
            recent_data.append("存在缺陷未进行消缺")
        if device.get("hidden_count") > 0:
            recent_data.append("存在隐患还未完成治理并验收")

        if recent_data:
            risk_desc.append(f"近90天内最近一次的数据显示, 该设备{','.join(recent_data)}。")

        # 历史数据
        history_data = []
        if device.get("fault_history_count") > 0:
            history_data.append("存在故障的历史记录")
        if device.get("defect_history_count") > 0:
            history_data.append("存在缺陷的历史记录")
        if device.get("hidden_history_count") > 0:
            history_data.append("存在隐患的历史记录")

        if history_data:
            risk_desc.append(f"根据历史同期的数据显示, 该设备{','.join(history_data)}。")

        if device.get("has_family_defect"):
            risk_desc.append("存在家族性缺陷")

        desc_str = "".join(risk_desc)
        if desc_str not in unique_descriptions:
            unique_descriptions.add(desc_str)
            device_risk_desc.append({
                "设备名称": device["device_name"],
                "设备类型": device["device_type_name"],
                "风险描述": desc_str
            })

    # 限制风险描述数量
    device_risk_desc = device_risk_desc[:10]

    # 构建判定依据
    judge_basis = {
        "线路导线类型": line_wire_des,
        "风险设备数描述": risk_devices_desc,
        "重过载": f"该线路在停电事件发生前处于{rated_date}运行状态" if "过载" in rated_date or "重载" in rated_date else ""
    }

    # 组装大模型输入参数
    model_input_params: Dict[str, Any] = {
        "设备类型统计": device_type_stats_new,
        "线路导线类型": line_wire_des,
        "风险设备数描述": risk_devices_desc,
        "重过载": judge_basis["重过载"],
        "设备风险描述": device_risk_desc,
        "判定依据": judge_basis,
        "存在风险的设备数": len(risk_devices),
        "outage_number": device_data.get("outageNumber", ""),
    }

    return {
        "code": 10000,
        "success": True,
        "data": model_input_params,
        "msg": "设备数据处理成功",
    }


__all__ = [
    "get_affiliated_psr_id",
    "safe_to_int",
    "calculate_device_risk",
    "build_tree_structure",
    "process_device_list",
    "normalize_psr_type",
    "get_device_category",
    "process_device_info_data",
]

