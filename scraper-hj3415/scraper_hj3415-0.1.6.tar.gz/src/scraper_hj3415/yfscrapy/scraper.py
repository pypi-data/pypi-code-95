import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from multiprocessing import Process, cpu_count

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.WARNING)


def chcwd(func):
    # scrapy는 항상 프로젝트 내부에서 실행해야하기때문에 일시적으로 현재 실행경로를 변경한다.
    def wrapper(*args, **kwargs):
        before_cwd = os.getcwd()
        logger.info(f'current path : {before_cwd}')
        after_cwd = os.path.dirname(os.path.realpath(__file__))
        logger.info(f'change path to {after_cwd}')
        os.chdir(after_cwd)
        func(*args, **kwargs)
        logger.info(f'restore path to {before_cwd}')
        os.chdir(before_cwd)
    return wrapper


@chcwd
def _run_scrapy(spider: str, ticker: str):
    # 본 코드를 직접 실행하지 않고 멀티프로세싱 함수에서 실행하도록 한다.
    # reference from https://docs.scrapy.org/en/latest/topics/practices.html(코드로 스파이더 실행하기)
    settings = get_project_settings()
    logger.info(f"bot name: {settings.get('BOT_NAME')}")
    process = CrawlerProcess(settings)
    process.crawl(spider, ticker=ticker)
    process.start()
