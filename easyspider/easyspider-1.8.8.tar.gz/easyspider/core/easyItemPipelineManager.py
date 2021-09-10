# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2018-03-05 19:46:37
# @Last Modified by:   hang.zhang
# @Last Modified time: 2018-03-05 19:47:56

from scrapy.pipelines import ItemPipelineManager


class easyItemPipelineManager(ItemPipelineManager):

    def process_item(self, item, spider, response):
        return self._process_chain('process_item', item, spider, response)
