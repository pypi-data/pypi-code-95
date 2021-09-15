"""
这个脚本包装了 Speed Test Cli
github: https://github.com/sivel/speedtest-cli/wiki

之后应该迁移到自建的测速工具上
"""

import logging
from typing import Optional

from rich.progress import Progress, BarColumn, TimeElapsedColumn, TaskID
from speedtest import Speedtest

from .data_type import SpeedResult

__all__ = ["do_speed_test", "do_speed_test_wrap"]


def speed_test_cb(progress: Progress, task_id: TaskID, idx: int, total: int, **kwargs):
    if kwargs.get("end") is True:
        progress.update(task_id, total=total, completed=idx + 1)


def do_speed_test_wrap(**kwargs) -> Optional[SpeedResult]:
    try:
        return do_speed_test(**kwargs)
    except Exception as e:
        log = logging.getLogger("rich")
        log.error(f"速度测试: {kwargs.get('server')} 失败: {e}")
        return None


def do_speed_test(
    server: Optional[str] = None,
    disable: Optional[str] = None,
    up_threads: Optional[int] = None,
    dl_threads: Optional[int] = None,
) -> SpeedResult:
    """
    进行 SpeedTest 测试

    服务器列表 ID 可以从这儿获取: https://williamyaps.github.io/wlmjavascript/servercli.html

    每次仅允许测试一个服务器

    :param server: 期望的服务器ID (ID 来自于 SpeedTest 官网)
    :param disable: up|down 禁止测试 上传/下载
    :param up_threads: 上传线程数量
    :param dl_threads: 下载线程数量
    """
    st = Speedtest()

    st.get_servers(servers=None if server is None else [server])

    server = st.best

    if disable != "up":
        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            "{task.completed} / {task.total}",
            TimeElapsedColumn(),
        ) as progress:
            task_id = progress.add_task(f"上传: {server['host']}")

            def up_cb(idx, total, **kwargs):
                speed_test_cb(progress, task_id, idx, total, **kwargs)

            st.upload(threads=up_threads, callback=up_cb)
    if disable != "dl":
        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            "{task.completed} / {task.total}",
            TimeElapsedColumn(),
        ) as progress:
            task_id = progress.add_task(f"下载: {server['host']}")

            def dl_cb(idx, total, **kwargs):
                speed_test_cb(progress, task_id, idx, total, **kwargs)

            st.download(threads=dl_threads, callback=dl_cb)

    return SpeedResult(**st.results.dict())
