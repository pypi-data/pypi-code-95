from typing import List

import click

from .data_type import PingResult
from .do_multi_ping import do_multi_ping
from .print_utils import print_ping_results

__all__ = ["init_ping_cli", "PingResult", "do_multi_ping"]


def init_ping_cli(main: click.Group):
    @main.group()
    def ping():
        """
        ping 测试
        """
        pass

    assert isinstance(ping, click.Group)

    @ping.command()
    @click.argument("host")
    def single(host: str):
        """
        ping 目标服务器

        例如: single www.baidu.com
        """
        results = do_multi_ping({host: None})
        print_ping_results(results)

    @ping.command()
    @click.option("--host", required=True, multiple=True, help="目的服务器IP, 允许多个值")
    def multi(host: List[str]):
        """
        ping 多个服务器

        例如: multi --host www.baidu.com --host www.google.com
        """

        results = do_multi_ping({h: None for h in host})
        print_ping_results(results)
