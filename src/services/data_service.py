"""数据服务调用模块"""
from typing import Any, Dict, Optional

import requests

from ..utils import config, logger


def post_to_data_service(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """向数据服务发送POST请求"""
    url = f"{config.normalized_base_url}/{path.lstrip('/')}"
    try:
        response = requests.post(
            url,
            json=payload,
            headers=config.build_headers(),
            timeout=config.timeout,
        )
        response.raise_for_status()
    except requests.Timeout as exc:
        logger.error(f"请求数据服务超时（{config.timeout}s）: {url}")
        raise RuntimeError(f"请求数据服务超时（{config.timeout}s）: {url}") from exc
    except requests.RequestException as exc:
        logger.error(f"请求数据服务失败: {url}")
        raise RuntimeError(f"请求数据服务失败: {url}") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError("数据服务返回的不是有效的 JSON。") from exc


def request_data_service(
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """向数据服务发送HTTP请求（支持GET和POST）"""
    url = f"{config.normalized_base_url}/{path.lstrip('/')}"

    request_args = {
        'url': url,
        'headers': config.build_headers(),
        'timeout': config.timeout,
    }

    if method.upper() == 'POST' and payload is not None:
        request_args['json'] = payload
    elif method.upper() == 'GET' and params is not None:
        request_args['params'] = params

    try:
        if method.upper() == 'POST':
            response = requests.post(**request_args)
        elif method.upper() == 'GET':
            response = requests.get(**request_args)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")

        response.raise_for_status()

    except requests.Timeout as exc:
        logger.error(f"{method}请求数据服务超时（{config.timeout}s）: {url}")
        raise RuntimeError(f"{method}请求数据服务超时（{config.timeout}s）: {url}") from exc
    except requests.RequestException as exc:
        logger.error(f"{method}请求数据服务失败: {url}")
        raise RuntimeError(f"{method}请求数据服务失败: {url}") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError("数据服务返回的不是有效的 JSON。") from exc


__all__ = ["post_to_data_service", "request_data_service"]

