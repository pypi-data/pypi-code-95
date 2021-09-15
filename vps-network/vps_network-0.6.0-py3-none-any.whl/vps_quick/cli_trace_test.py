import logging
from typing import Optional, List

from ..vps_api import NetworkApi
from ..vps_api.dt import TraceForm
from ..vps_trace import TraceResult, do_traceroute_v2_wrapper

__all__ = ["cli_do_trace"]


def cli_do_trace(
    hosts: List[str],
    trace_count: int,
    interval: float,
    timeout: int,
    trace_hops: int,
    job_id: Optional[str],
    api: NetworkApi,
    log: logging.Logger,
):
    log.info(f"开始执行 traceroute {hosts} ...")
    trace_results: List[TraceResult] = []
    for host in hosts:
        p = do_traceroute_v2_wrapper(
            host=host,
            count=trace_count,
            interval=interval,
            timeout=timeout,
            max_hops=trace_hops,
        )
        if p is None:
            continue
        trace_results.append(p)

    trace_form = TraceForm(job_id=job_id, results=trace_results)
    ret = api.trace_report(trace_form)
    if ret.errno == 0:
        log.info("上报 Traceroute 测试结果成功")
    else:
        log.error(f"上报 traceroute 结果失败: {ret}")
