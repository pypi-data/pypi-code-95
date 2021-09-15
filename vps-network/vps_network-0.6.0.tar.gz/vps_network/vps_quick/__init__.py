"""
快速进行测试
"""

import logging
import os
import sys
from typing import Optional

import click
from rich.logging import RichHandler

from .cli_php_test import cli_php_test
from .cli_ping_test import cli_do_ping
from .cli_speed_test import cli_do_speed_test
from .cli_trace_test import cli_do_trace
from ..vps_api import NetworkApi
from ..vps_speed import (
    get_cn_server_list,
    get_oversea_server_list,
    get_cc_server_list,
)

__all__ = ["init_quick_cli"]


def init_quick_cli(main: click.Group):  # noqa
    @main.command()
    @click.option(
        "--app-key",
        type=str,
        required=True,
        help="上报数据的APPKey",
        default=lambda: os.environ.get("BENCH_APP_KEY", "").strip(),
        show_default="BENCH_APP_KEY",
    )
    @click.option(
        "--job-id",
        type=str,
        help="测试任务的ID",
        default=lambda: os.environ.get("VPS_JOB_ID", None),
    )
    @click.option("--out-dir", type=str, help="测试结果写入到目标目录")
    @click.option("--cc", type=str, help="测试目标国家,没有设置则随机选择 国内 和 海外")
    @click.option("--limit", type=int, help="要测试多少个服务器", default=16)
    @click.option("--ping-count", type=int, help="Ping 测试发送数据包的数量", default=8)
    @click.option("--trace-hops", type=int, help="Traceroute 最大跳", default=32)
    @click.option("--trace-count", type=int, help="Traceroute 发送数据包的数量", default=2)
    @click.option(
        "--interval", type=float, help="Ping/Trace 测试发送数据包的间隔时间", default=0.05
    )
    @click.option("--timeout", type=int, help="Ping/Trace 测试超时时间", default=3)
    @click.option(
        "--speed-disable",
        type=click.Choice(["up", "dl"], case_sensitive=False),
        help="禁止 上传/下载 测试, 不允许同时禁止",
    )
    @click.option("--no-ping-test", is_flag=True, help="不进行 Ping 测试")
    @click.option("--no-trace-test", is_flag=True, help="不进行 Traceroute 测试")
    @click.option("--no-speed-test", is_flag=True, help="不进行 Speed 测试")
    @click.option("--no-php", is_flag=True, help="不进行 php 测试")
    def quick(
        app_key: str,
        job_id: Optional[str],
        out_dir: Optional[str],
        cc: Optional[str],
        limit: Optional[int],
        ping_count: int,
        trace_hops: int,
        trace_count: int,
        interval: float,
        timeout: int,
        speed_disable: Optional[str],
        no_ping_test: bool,
        no_trace_test: bool,
        no_speed_test: bool,
        no_php: bool,
    ):
        """
        VPS 网络快速测试
        """
        logging.basicConfig(  # noqa
            level="NOTSET",
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler()],
        )

        log = logging.getLogger("rich")
        if len(app_key) == 0:
            log.error("没有配置 app key")
            sys.exit(2)

        job_id = None if job_id in ("", None) else job_id.strip()

        api = NetworkApi(app_key, out_dir=out_dir)

        # get server list
        log.info("开始获取服务器列表...")
        if cc is None:
            cn_list = get_cn_server_list(None, limit)
            oversea_list = get_oversea_server_list(None, limit)
            server_list = cn_list + oversea_list
        else:
            server_list = get_cc_server_list(cc, limit)

        if len(server_list) == 0:
            log.error("获取服务器列表失败")
            sys.exit(1)

        log.info(f"获取服务器列表成功: {server_list}")

        host_cc_dict = dict()
        for item in server_list:
            host_cc_dict[item.host.split(":")[0]] = item.cc

        if not no_ping_test:
            cli_do_ping(
                hosts=host_cc_dict,
                log=log,
                ping_count=ping_count,
                interval=interval,
                timeout=timeout,
                job_id=job_id,
                api=api,
            )

        hosts = []
        for item in server_list:
            hosts.append(item.host.split(":")[0])

        if not no_trace_test:
            cli_do_trace(
                hosts=hosts,
                trace_count=trace_count,
                interval=interval,
                timeout=timeout,
                trace_hops=trace_hops,
                job_id=job_id,
                api=api,
                log=log,
            )

        if not no_speed_test:
            cli_do_speed_test(
                server_list=server_list,
                job_id=job_id,
                api=api,
                speed_disable=speed_disable,
                log=log,
            )

        if not no_php:
            cli_php_test(api=api, job_id=job_id)
