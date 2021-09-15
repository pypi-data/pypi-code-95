import statistics
from typing import List

from rich.console import Console
from rich.table import Table

from .data_type import PingResult

__all__ = ["print_ping_results"]


def print_ping_results(results: List[PingResult]):
    """
    打印 ping 测试结果
    """

    table = Table(title="Ping 测试结果 (时间单位: ms)")
    table.add_column("IP", justify="right", style="cyan", no_wrap=True)
    table.add_column("国家", justify="right")
    table.add_column("最小RTT", justify="right")
    table.add_column("最大RTT", justify="right")
    table.add_column("平均RTT", justify="right")
    table.add_column("标准差", justify="right")
    table.add_column("失败", style="red")
    table.add_column("成功", style="green")

    for ret in results:
        success = list(filter(lambda x: x is not None, ret.times))
        if len(success) == 0:
            success = [0, 0]

        failure = ret.count - len(ret.times)
        row = [
            ret.host,
            ret.cc,
            f"{min(success):.2f}",
            f"{max(success):.2f}",
            f"{statistics.mean(success):.2f}",
            f"{statistics.stdev(success):.2f}",
            str(failure),
            str(len(ret.times)),
        ]
        table.add_row(*row)

    console = Console()
    console.print(table)
