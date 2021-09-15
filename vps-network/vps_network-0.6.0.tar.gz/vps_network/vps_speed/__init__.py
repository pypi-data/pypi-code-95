from typing import Optional, List

import click

from .data_type import SpeedResult, SpeedServer, SpeedClient
from .do_speedtest import do_speed_test, do_speed_test_wrap
from .get_list import (
    get_server_list,
    get_cn_server_list,
    get_oversea_server_list,
    get_cc_server_list,
    ServerInfo,
)
from .utils import print_server_list, print_speed_test_result

__all__ = [
    "init_speed_test_cli",
    "do_speed_test",
    "do_speed_test_wrap",
    "get_cn_server_list",
    "get_oversea_server_list",
    "get_cc_server_list",
    "SpeedResult",
    "SpeedServer",
    "SpeedClient",
    "ServerInfo",
]


def init_speed_test_cli(main: click.Group):
    @main.group()
    def speedtest():
        """
        网络速度(SpeedTest)测试
        """
        pass

    assert isinstance(speedtest, click.Group)

    @speedtest.command(name="cn-list")
    @click.option(
        "--server",
        multiple=True,
        help="期望使用的 SpeedTest 目标服务器, 注意: 这个值是 SpeedTest 测试服务器的 ID",
    )
    @click.option("--limit", type=int, help="最多获取多少条数据")
    def cn_server_list(server: Optional[List[str]], limit: Optional[int]):
        """
        获取中国的服务器列表
        """
        ret = get_cn_server_list(servers=server, limit=limit)
        print_server_list(ret)

    @speedtest.command(name="list")
    @click.option(
        "--server",
        multiple=True,
        help="期望使用的 SpeedTest 目标服务器, 注意: 这个值是 SpeedTest 测试服务器的 ID",
    )
    @click.option("--cc", multiple=True, help="使用国家过滤服务器")
    @click.option("--limit", type=int, help="最多获取多少条数据")
    def server_list(
        server: Optional[List[str]], cc: Optional[List[str]], limit: Optional[int]
    ):
        """
        获取 SpeedTest 服务器列表
        """
        cc = set() if cc is None else set(map(lambda v: v.upper(), cc))

        ret = get_server_list(servers=server)

        if len(cc) > 0:
            ret = list(filter(lambda x: x.cc.upper() in cc, ret))

        if limit is not None:
            ret = ret[:limit]

        print_server_list(ret)

    @speedtest.command(name="test")
    @click.option(
        "--server",
        help="期望使用的 SpeedTest 目标服务器, 注意: 这个值是 SpeedTest 测试服务器的 ID",
    )
    @click.option(
        "--disable",
        type=click.Choice(["up", "dl"], case_sensitive=False),
        help="禁止 上传/下载 测试, 不允许同时禁止",
    )
    @click.option("--up-threads", type=int, help="上传线程数量")
    @click.option("--dl-threads", type=int, help="下载线程数量")
    def speed_test(
        server: Optional[str],
        disable: Optional[str],
        up_threads: Optional[int],
        dl_threads: Optional[int],
    ):
        """
        网络速度测试

        服务器列表 ID 可以尝试从这儿获取: https://williamyaps.github.io/wlmjavascript/servercli.html
        """

        ret = do_speed_test(
            server=server, disable=disable, dl_threads=dl_threads, up_threads=up_threads
        )

        print_speed_test_result(ret)
