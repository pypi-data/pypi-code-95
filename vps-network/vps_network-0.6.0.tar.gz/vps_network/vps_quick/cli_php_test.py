import logging
from typing import Optional

from ..vps_api import NetworkApi
from ..vps_api.dt import PhpForm
from ..vps_php import do_php_compile

__all__ = ["cli_php_test"]


def cli_php_test(api: NetworkApi, job_id: Optional[str]):
    result = do_php_compile()

    logger = logging.getLogger("rich")
    logger.info(f"测试结果: {result}")

    form = PhpForm(job_id=job_id, result=result)
    if api is not None:
        logger.info("上报 PHP 结果")
        v = api.php_report(form)
        if v is not None and v.errno == 0:
            logger.info("上报结果成功")
        else:
            logger.error(f"上报结果失败: {v}")
    else:
        logger.info("不需要上报结果")
