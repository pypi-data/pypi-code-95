import click
from rich.console import Console
from rich.live import Live
from rich.table import Table

from .data_type import TraceHop, TraceResult
from .do_traceroute import do_traceroute
from .do_traceroute_v2 import do_traceroute_v2, do_traceroute_v2_wrapper

__all__ = [
    "init_traceroute_cli",
    "TraceHop",
    "TraceResult",
    "do_traceroute_v2",
    "do_traceroute_v2_wrapper",
]


def init_traceroute_cli(main: click.Group):
    @main.command()
    @click.option("--host", required=True, help="目标服务器")
    @click.option("--count", type=int, default=2, help="每个IP地址发送多少个Ping请求")
    @click.option("--hops", type=int, default=32, help="最多多少跳(TCP time to live)")
    @click.option("--fast", is_flag=True, help="快速模式")
    def traceroute(host: str, count: int, hops: int, fast: bool):
        """
        traceroute [host]

        traceroute 目的主机测试

        注意: 这个程序需要使用 Root 运行
        """
        console = Console()

        addr = host

        table = Table(title=f"Traceroute ({addr}) 测试", show_lines=True)
        table.add_column("IP", justify="right")
        table.add_column("位置", justify="right")
        table.add_column("ISP", justify="right")
        table.add_column("最小RTT", justify="right")
        table.add_column("平均RTT", justify="right")
        table.add_column("最大RTT", justify="right")

        with Live(
            table,
            console=console,
            refresh_per_second=8,
            transient=True,
            vertical_overflow="visible",
        ):
            result = do_traceroute(
                table=table, address=addr, count=count, max_hops=hops, fast=fast
            )
            print(result)
        print("\n" * 60)
        console.clear()
        console.print(table)
