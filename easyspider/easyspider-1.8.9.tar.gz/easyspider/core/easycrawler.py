# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2017-07-28 11:25:11
# @Last Modified by:   hang.zhang
# @Last Modified time: 2018-03-04 13:51:48

"""
    替换这个的最终目的就是替换引擎和scraper
    为了减少代码量，要上多继承了
    Crawler <- Object
    CrawlerRunner <- Object
    CrawlerProcess <- CrawlerRunner
    关系是 CrawlerRunner 会调用Crawler 从而把三个连起来了
    python 新式类的多继承是：从左到右，宽度优先 (经典类是从左至右，深度优先)
"""


import time
import six
import sys
import logging
from twisted.internet import defer
from scrapy.utils.misc import load_object
from scrapy.crawler import CrawlerProcess, Crawler, CrawlerRunner


logger = logging.getLogger(__name__)

settings_engine_key = "ENGINE"
default_engine = "scrapy.core.engine.ExecutionEngine"


class easyCrawler(Crawler):

    def _create_engine(self):
        """最终目的只是为了替换这个，前面的工作只是为了替换这个
        """
        # 核心变更行 在这里检查settings 是否有写明engine, 否则使用默认的原scrapy engine
        engine = self.settings.get(settings_engine_key, default_engine)
        engine_cls = load_object(engine)
        # return easyExecutionEngine(self, lambda _: self.stop())
        return engine_cls(self, lambda _: self.stop())

    @defer.inlineCallbacks
    def crawl(self, *args, **kwargs):
        """allow spider can return None in start_requests"""
        assert not self.crawling, "Crawling already taking place"
        self.crawling = True

        try:
            self.spider = self._create_spider(*args, **kwargs)
            self.engine = self._create_engine()

            # scrapy's source
            # start_requests = iter(self.spider.start_requests())
            # yield self.engine.open_spider(self.spider, start_requests)

            # modified to:
            start_requests = self.spider.start_requests() or ()
            start_requests = iter(start_requests)
            while True:
                try:
                    # don't close spider in any time !!!!
                    # because sometime adsl server can't not access net, and wrong cause queue empty then let close spider
                    yield self.engine.open_spider(self.spider, start_requests)
                    break
                except Exception:
                    time.sleep(3)
                    logger.exception("error in start spider: self.engine.open_spider")

            yield defer.maybeDeferred(self.engine.start)
        except Exception:
            if six.PY2:
                exc_info = sys.exc_info()

            self.crawling = False
            if self.engine is not None:
                yield self.engine.close()

            if six.PY2:
                six.reraise(*exc_info)
            raise


class easyCrawlerRunner(CrawlerRunner):

    def _create_crawler(self, spidercls):
        if isinstance(spidercls, six.string_types):
            spidercls = self.spider_loader.load(spidercls)
        return easyCrawler(spidercls, self.settings)


class easyCrawlerProcess(CrawlerProcess, easyCrawlerRunner):
    """虽然是多继承，但是实际上CrawlerProcess 和 CrawlerRunner没有重名的方法，定好顺序只是为了以防万一
    """
    pass
