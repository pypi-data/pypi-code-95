# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2018-04-04 17:52:25
# @Last Modified by:   hang.zhang
# @Last Modified time: 2018-04-04 17:54:10

from scrapy.statscollectors import MemoryStatsCollector


class easyspiderStatsCollector(MemoryStatsCollector):

    def __init__(self, crawler):

        super(easyspiderStatsCollector, self).__init__(crawler)
