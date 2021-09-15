from typing import List

from rich.console import Console
from rich.table import Table

from .data_type import SpeedResult
from .get_list import ServerInfo

__all__ = ["print_server_list", "print_speed_test_result"]


def print_server_list(ret: List[ServerInfo]) -> None:
    """
    打印出服务器的列表信息
    :param ret: 服务器列表
    """
    table = Table(title="SpeedTest 服务器列表", show_lines=True)

    table.add_column("ID")
    table.add_column("名称")
    table.add_column("国家\n经纬度")
    table.add_column("Host")

    for x in ret:
        table.add_row(
            f"{x.id}",
            x.name,
            f"{x.cc}\n{x.lat}\n{x.lon}",
            x.host,
        )

    console = Console()
    console.print(table)


def print_speed_test_result(ret: SpeedResult):
    console = Console()

    server = ret.server
    table = Table(title=f"SpeedTest ({ret.server.host}) 测试结果")
    table.add_column("字段")
    table.add_column("值")

    # 服务器信息
    table.add_row("服务器信息", style="bold")
    table.add_row("ID", server.id)
    table.add_row("URL", server.url)
    table.add_row("经纬度", f"({server.lat}, {server.lon})")
    table.add_row("名称", server.name)
    table.add_row("国家", server.country)
    table.add_row("赞助商", server.sponsor)

    # 客户端信息
    client = ret.client
    table.add_row("客户端信息", style="bold")
    table.add_row("IP", client.ip)
    table.add_row("经纬度", f"({client.lat}, {client.lon})")
    table.add_row("ISP", client.isp)
    table.add_row("国家", client.country)

    # 测试结果
    table.add_row("测试结果", style="bold")
    table.add_row("下载速度", f"{ret.download:.2f}")
    table.add_row("上传速度", f"{ret.upload:.2f}")
    table.add_row("ping", f"{ret.ping:.2f}")
    table.add_row("测试时间", ret.timestamp)
    table.add_row("发送数据量", f"{ret.bytes_sent}")
    table.add_row("接收数据量", f"{ret.bytes_received}")
    console.print(table)
