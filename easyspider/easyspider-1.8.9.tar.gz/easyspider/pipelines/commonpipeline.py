# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2018-03-05 20:23:52
# @Last Modified by:   hhczy
# @Last Modified time: 2019-12-07 23:17:07
import copy
import json
from scrapy.utils.request import referer_str
from twisted.internet.threads import deferToThread


class commonpipeline(object):
    """通过继承 commonpipeline 来保证

    1. pipeline 是异步同时进行的
    2. 一旦出错，能及时汇报上去，汇报到 failed_urls

    注意, commonpipeline 调用的都是 _process_item  前面有一个 _ 下划线
    """

    def process_item(self, item, spider, response):
        # return self._process_item(item, spider, response)
        # d = deferToThread(self._process_item, item, spider, response)
        # 一定要copy 否则数量会不对，执行的快了，item会相互影响
        copy_item = copy.deepcopy(item)
        # self._process_item(copy_item, spider, response)
        # return copy_item
        d = deferToThread(self._process_item, copy_item, spider, response)

        def error_back(err):
            # 既然出错，那么就要block_callback记录，重新放回起始队列
            r_copy = response.copy()
            # 如果直接从 yiled Reuest 过来的话，那就是没有带上 easyspider 信息的
            if "easyspider" not in r_copy.request.meta:
                r_copy.request.meta["easyspider"] = {"from_retry": 1}
            else:
                r_copy.request.meta["easyspider"]["from_retry"] += 1
            # 带上item 方便检查错误在哪
            # msg = "Error processing %s ; %s" % (json.dumps(item), err.getTraceback())
            msg = {
                "request": "%(request)s (referer: %(referer)s)" % {'request': response.request, 'referer': referer_str(response.request)},
                "body": spider.get_unicode_response_body(response),
                "traceback": "Error processing %s ; %s" % (json.dumps(copy_item), err.getTraceback())
            }
            spider.put_back_2_start_url(r_copy,
                                        exc_info=msg,
                                        )
            return copy_item
        d.addErrback(error_back)
        return d
