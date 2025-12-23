"""报文数据处理服务"""
import json
from typing import Any, Dict, List

from ..utils import logger


def get_condition(wave_obj: Dict[str, Any]) -> str:
    """获取故障条件"""
    return wave_obj.get("condition", "")


def get_wave_fault_type(condition: str, current_type: int) -> int:
    """根据故障条件获取故障类型"""
    if not condition:
        return current_type

    if "三相" in condition:
        return 4
    elif "接地" in condition:
        return 2
    elif "短路" in condition:
        return 3
    elif "断线" in condition:
        return 1

    return current_type


def clean_result(result: str) -> str:
    """清理结果字符串"""
    if not result:
        return ""

    # 分割并处理每一部分
    parts = result.split("\n\n")
    cleaned_parts = []

    for part in parts:
        # 替换各种特殊字符和标记
        cleaned = (
            part.replace("#", "")
            .replace("\\n", "")
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )
        if cleaned:  # 只保留非空部分
            cleaned_parts.append(cleaned)

    # 重新组合
    return "".join(cleaned_parts)


def process_message_data(res: str, wave_data_str: str) -> Dict[str, Any]:
    """处理报文和录波数据"""
    logger.info(f"报文数据: {res}")
    logger.info(f"录波数据: {wave_data_str}")

    try:
        # 解析JSON数据
        res_data = json.loads(res)
        wave_data = json.loads(wave_data_str)

        # 获取数据数组
        data = res_data.get("data", [])
        wave_data_list = wave_data.get("data", [])

        # 处理录波数据
        wave_analysis = "无数据"
        wave_fault_type = 5  # 默认值

        if wave_data_list and len(wave_data_list) > 0:
            wave_obj = wave_data_list[0]
            condition = get_condition(wave_obj)
            line_id = wave_obj.get("lineId", "未知线路")
            wave_analysis = f"根据录波数据显示, 10kV{line_id}发生{condition}故障"
            wave_fault_type = get_wave_fault_type(condition, wave_fault_type)

        # 构建处理文本
        builder_parts = ["[故障简述] : 无;"]

        # 过滤和处理SOE数据
        filtered_data = []
        if isinstance(data, list):
            for item in data[:50]:  # 限制50条
                if isinstance(item, dict):
                    content = item.get("content")
                    if content and str(content).strip():
                        filtered_data.append(item)

        if filtered_data:
            soe_results = []
            for i, obj in enumerate(filtered_data):
                if i > 0:
                    soe_results.append("，")
                start_time = obj.get("startTime", "")
                content = obj.get("content", "")
                soe_results.append(f"{start_time} {content}")

            soe_text = "".join(soe_results)

            builder_parts.append(f"[故障录波判定结果] : {wave_analysis}")
            builder_parts.append("[故障前后一段时间稳态波形] : 无.")
            builder_parts.append(f"[SOE序列]{soe_text};")

        elif wave_data_list:
            builder_parts.append(f"[故障录波判定结果] : {wave_analysis}")
            builder_parts.append("[故障前后一段时间稳态波形] : 无.")
            builder_parts.append("[SOE序列] : 无.")

        # 清理结果
        result_text = "".join(builder_parts)
        cleaned_result = clean_result(result_text)

        return {
            "code": 10000,
            "success": True,
            "data": cleaned_result,
            "msg": "处理成功"
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {e}")
        return {
            "code": 500,
            "success": False,
            "data": None,
            "msg": f"JSON解析失败: {str(e)}"
        }
    except Exception as e:
        logger.error(f"处理报文智能体信息时发生错误: {e}")
        return {
            "code": 500,
            "success": False,
            "data": None,
            "msg": f"处理失败: {str(e)}"
        }


__all__ = [
    "get_condition",
    "get_wave_fault_type",
    "clean_result",
    "process_message_data",
]

