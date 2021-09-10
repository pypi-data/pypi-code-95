# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2017-07-28 13:54:28
# @Last Modified by:   hang.zhang
# @Last Modified time: 2018-03-04 13:52:32
from scrapy.core.engine import ExecutionEngine
from scrapy.utils.misc import load_object
import logging

logger = logging.getLogger(__name__)

scraper_key = "SCRAPER"
default_scraper = "scrapy.core.scraper.Scraper"


class easyEngine(ExecutionEngine):

    def __init__(self, crawler, spider_closed_callback):
        """ExecutionEngine 在初始化的时候定义了scraper
        这里等他初始化完了,再更改过来了,就无需复制之前的初始化代码
        """
        super(easyEngine, self).__init__(crawler, spider_closed_callback)

        scraper = self.settings.get(scraper_key, default_scraper)
        scraper_cls = load_object(scraper)
        self.scraper = scraper_cls(crawler)
