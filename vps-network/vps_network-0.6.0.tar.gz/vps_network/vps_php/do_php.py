import logging
import os
import subprocess
import time
from typing import Optional

from .data_type import PhpCompileResult

__all__ = ["do_php_compile"]


def do_php_compile() -> Optional[PhpCompileResult]:
    logger = logging.getLogger("rich")
    logger.info("开始 PHP 编译测试")

    start_time = time.time()
    try:
        subprocess.run("/php/php.bash", check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"PHP 编译失败: {e}")
        return
    end_time = time.time()

    diff_time = end_time - start_time
    return PhpCompileResult(time=diff_time, version=os.getenv("PHP_VERSION"))
