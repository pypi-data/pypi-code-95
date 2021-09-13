"""
从 HTTP Header 中获取的信息
"""
from typing import Optional

from django.http import HttpRequest

__all__ = ["get_client_ip"]


def get_client_ip(request: HttpRequest) -> Optional[str]:
    """
    获取用户的 IP 地址
    """

    x: str = request.META.get("HTTP_X_FORWARDED_FOR", None)
    if x:
        return x.split(",")[0]
    return request.META.get("REMOTE_ADDR", None)
