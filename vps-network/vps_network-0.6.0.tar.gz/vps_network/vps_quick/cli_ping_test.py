import logging
from typing import Optional

from ..vps_api import NetworkApi
from ..vps_api.dt import PingForm
from ..vps_ping import do_multi_ping

__all__ = ["cli_do_ping"]


def cli_do_ping(
    hosts: dict,  # dict of ip to CC
    log: logging.Logger,
    ping_count: int,
    interval: float,
    timeout: int,
    job_id: Optional[str],
    api: NetworkApi,
):
    log.info(f"ping 测试 {hosts}....")
    ping_result = do_multi_ping(
        hosts, count=ping_count, interval=interval, timeout=timeout
    )

    ping_form = PingForm(job_id=job_id, results=ping_result)
    ret = api.ping_report(ping_form)
    if ret is not None and ret.errno == 0:
        log.info("上报 Ping 测试结果成功")
    else:
        log.error(f"上报 Ping 结果失败: {ret}")
