import logging
from typing import Optional, List

from ..vps_api import NetworkApi
from ..vps_api.dt import SpeedForm
from ..vps_speed import do_speed_test_wrap, ServerInfo

__all__ = ["cli_do_speed_test"]


def cli_do_speed_test(
    server_list: List[ServerInfo],
    job_id: Optional[str],
    api: NetworkApi,
    speed_disable: Optional[str],
    log: logging.Logger,
):
    all_list = server_list

    # do speed test
    speed_result = []
    for item in all_list:
        log.info(f"速度测试: {item.name} {item.sponsor} {item.host}")
        v = do_speed_test_wrap(server=str(item.id), disable=speed_disable)
        if v is None:
            log.error(f"速度测试: {item.name}({item.host=}, {item.id=}) 失败")
        else:
            log.info(f"速度测试: {item.name} 已完成")
            speed_result.append(v)

    speed_form = SpeedForm(job_id=job_id, results=speed_result)
    ret = api.speed_report(speed_form)
    if ret.errno == 0:
        log.info("上报速度测试结果成功")
    else:
        log.error(f"上报速度测试结果失败: {ret}")
