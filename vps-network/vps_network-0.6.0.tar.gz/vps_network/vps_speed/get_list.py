"""
这个脚本包装了 Speed Test Cli
github: https://github.com/sivel/speedtest-cli/wiki

之后应该迁移到自建的 SpeedTest 工具上
"""

import random
from typing import Optional, List

from pydantic import BaseModel, Field
from speedtest import Speedtest

__all__ = [
    "get_server_list",
    "get_oversea_server_list",
    "get_cn_server_list",
    "get_cc_server_list",
    "ServerInfo",
]


class ServerInfo(BaseModel):
    url: str = Field(..., title="网址")
    lat: str = Field(..., title="经度")
    lon: str = Field(..., title="纬度")
    name: str = Field(..., title="名称")
    country: str = Field(..., title="国家")
    cc: str = Field(..., title="国家缩写")
    sponsor: str = Field(..., title="赞助商")
    id: str = Field(..., title="SpeedTest ID")
    host: str = Field(..., title="服务器地址")
    d: float = Field(..., title="延迟", description="单位: 毫秒")


def get_cn_server_list(
    servers: Optional[List[str]] = None, limit: Optional[int] = None
) -> List[ServerInfo]:
    """
    获取中国的服务器列表
    """
    ret = get_server_list(servers=servers)
    ret = list(filter(lambda x: x.cc.upper() == "CN", ret))
    if limit is not None:
        ret = ret[:limit]
    return ret


def get_oversea_server_list(
    servers: Optional[List[str]] = None, limit: Optional[int] = None
):
    """
    获取海外的服务器列表
    """
    ret = get_server_list(servers=servers)
    ret = list(filter(lambda x: x.cc.upper() != "CN", ret))
    if limit is not None:
        ret = ret[:limit]
    return ret


def get_cc_server_list(cc: str, limit: Optional[int] = None):
    """
    获取指定国家的测速节点
    """
    ret = get_server_list()
    ret = list(filter(lambda x: x.cc.upper() == cc.upper(), ret))
    if limit is not None:
        ret = ret[:limit]
    return ret


def get_server_list(servers: Optional[List[str]] = None) -> List[ServerInfo]:
    """
    进行 SpeedTest 测试

    服务器列表 ID 可以从这儿获取: https://williamyaps.github.io/wlmjavascript/servercli.html

    :param servers: 期望的服务器列表ID (不是目标服务器)
    :return: dict
    """
    st = Speedtest()
    servers = st.get_servers(servers=servers)
    ret = []
    for key, value in servers.items():
        ret += value
    random.shuffle(ret)  # ensure we keep some random
    return list(map(lambda x: ServerInfo(**x), ret))
