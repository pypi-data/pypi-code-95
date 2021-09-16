# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2017-07-28 14:07:10
# @Last Modified by:   hhczy
# @Last Modified time: 2019-12-07 23:16:45
import sys
if sys.version_info < (3, ):
    reload(sys)
    sys.setdefaultencoding("utf-8")
import os
import json
import logging
import traceback
from scrapy import signals
from scrapy.http import Request
from scrapy.item import BaseItem
from scrapy_redis import picklecompat
from scrapy.exceptions import DropItem
from scrapy.core.scraper import Scraper
from twisted.python.failure import Failure
from scrapy.utils.request import referer_str
from scrapy.utils.reqser import request_to_dict
from scrapy.utils.log import failure_to_exc_info
from scrapy.utils.log import logformatter_adapter
from scrapy.utils.request import request_fingerprint


logger = logging.getLogger(__name__)


class easyScraper(Scraper):

    # 核心希望替换的东西
    def handle_spider_error(self, _failure, request, response, spider):
        """
            目的就是要在出错的时候，能够打印出出错的body请求。同时把出错的请求，重新放回队列中去
            预防这样一种情况：当出现正则或者xpath规则提取不到的时候，能够马上反映出，是为什么规则出错
            是否是发现了不同格式的body内容，需要增加规则的数量
            而常规的scraper 只是记录报错写error log和reason，并不会告诉你此时的response body
            由于blocked之后的操作和此次目的是一样的，所以直接就用这个
        """

        super(easyScraper, self).handle_spider_error(_failure, request, response, spider)
        # traceback_msg = _failure.getErrorMessage()
        traceback_msg = "%s, %s" % (failure_to_exc_info(_failure), repr(traceback.format_exc()))
        if os.name == "nt":
            traceback_msg = traceback_msg.decode("gbk")
        msg = {
            "request": "%(request)s (referer: %(referer)s)" % {'request': request, 'referer': referer_str(request)},
            "body": spider.get_unicode_response_body(response),
            "traceback": traceback_msg
        }
        """
        msg = "Spider error processing %(request)s (referer: %(referer)s): response body %(body)s  traceback %(traceback)s" % {'request': request,
                                                                                                                               "referer": referer_str(request),
                                                                                                                               "body": spider.get_unicode_response_body(response),
                                                                                                                               "traceback": traceback_msg
                                                                                                                               }
        """
        spider.blocked_call_back(response,
                                 reason="Spider error processing %(request)s (referer: %(referer)s): info %(info)s" % {'request': request, 'referer': referer_str(request), 'info': "%s, %s" % (failure_to_exc_info(_failure), repr(traceback.format_exc()))},
                                 exc_info=msg,
                                 extra=self.__class__.__name__)

    # Error downloading 就不需要记录，因为Error downloading根本没有body
    # def _log_download_errors(self, spider_failure, download_failure, request, spider):
    #     pass

    def _process_spidermw_output(self, output, request, response, spider):
        """给pipeline结果添加response参数，这样方便根据response回推
        add response argument in item pipeline
        """
        if isinstance(output, Request):
            meta_easyspider = output.meta.get("easyspider") or {}
            meta_easyspider.update({
                "crawled_urls_path": meta_easyspider.get("crawled_urls_path", []) + [request.url]
            })
            output.meta.update({"easyspider": meta_easyspider})
            self.crawler.engine.crawl(request=output, spider=spider)
        elif isinstance(output, (BaseItem, dict)):
            self.slot.itemproc_size += 1
            # this if will never be false, because the only time to be false, is request from put_back_2_start_urls, and history request has meta..and has
            # crawled_urls_path...but, ! put_back_2_start_urls will not record crawled_urls_path
            # -----------------------------------------------
            if not output.get("crawled_url"):
                """正常情况下，应该都是没有 crawled_url, 从来都不可能进入到下面的else判断

                因为只有在这里，才会被加上crawled_url，而能进入这里，要么下一步就是成功，要么下一步就是失败。
                """
                output["crawled_url"] = response.url

                meta_easyspider = response.meta.get("easyspider") or {}

                # 写入整个爬虫的路径过程，如果预先就有请求过程，那么就在之前的请求过程后面追加
                crawled_urls_path = meta_easyspider.get("crawled_urls_path") or []
                if not response.meta.get("redirect_urls"):
                    # 如果没有被跳转的情况下，就是当前的链接，加上历史的请求过程
                    crawled_urls_path = crawled_urls_path + [response.url]
                else:
                    # 有跳转，那么跳转的路径，也需要记录
                    crawled_urls_path = crawled_urls_path + response.meta.get("redirect_urls")
                # 回写进去数据结果，保存整个爬虫的经历路径
                output["crawled_urls_path"] = crawled_urls_path
            else:
                """是不可能进入这个判断的 ！！！
                """
                output["crawled_urls_path"] = response.meta.get("easyspider", {}).get("crawled_urls_path") or []
                output["crawled_urls_path"] += [response.url]
            # -----------------------------------------------
            # 重大改变： 添加了response参数，方便回推
            dfd = self.itemproc.process_item(output, spider, response)
            dfd.addBoth(self._itemproc_finished, output, response, spider)
            return dfd
        elif output is None:
            # 强制要求，必须输出结果，哪怕是一个空的 {}
            # 不输出结果的话，就不会加入dupefilter，将会别其他爬虫或者它自己重复性消费
            # 这样做的目的是精细化抓取，避免因为被屏蔽等原因，虽然正常，但是没有获得结果
            # 导致链接丢失，从而丢掉数据
            pass
        else:
            typename = type(output).__name__
            logger.error('Spider must return Request, BaseItem, dict or None, '
                         'got %(typename)r in %(request)s',
                         {'request': request, 'typename': typename},
                         extra={'spider': spider})

    def _itemproc_finished(self, output, item, response, spider):
        """pipeline 全部处理完之后，就该是标记已经完成，即 添加进pipeline
        (只有当全部的流程，全部的pipeline走完，仍然没问题，才能被标记成功)

        ItemProcessor finished for the given ``item`` and returned ``output``
        """
        self.slot.itemproc_size -= 1
        # -------------------------
        rq = response.request
        # --------------------------
        if isinstance(output, Failure) or not rq:
            """另外一种常见的情况就是，在处理pipeline的时候出问题了
            比如说 DataError: (_mysql_exceptions.DataError) (1406, "Data too long for column 'categories' at row 1")
            此时就不应该添加successed_url 而是直接提交到failed_url 去保存来报警
            并且不应该添加 【dupefilter】
            (不添加很难做，暂时添加，后面把 failed_url 重新放回start_urs的时候，给定dont_filter=True来解决这个问题)
            """
            ex = output.value
            if isinstance(ex, DropItem):
                logkws = self.logformatter.dropped(item, ex, response, spider)
                logger.log(*logformatter_adapter(logkws), extra={'spider': spider})
                return self.signals.send_catch_log_deferred(
                    signal=signals.item_dropped, item=item, response=response,
                    spider=spider, exception=output.value)
            else:
                logger.error('Error processing %(item)s', {'item': item},
                             exc_info=failure_to_exc_info(output),
                             extra={'spider': spider})
                # 既然出错，那么就要block_callback记录，重新放回起始队列
                r_copy = response.copy()
                # 如果直接从 yiled Reuest 过来的话，那就是没有带上 easyspider 信息的
                if "easyspider" not in r_copy.request.meta:
                    r_copy.request.meta["easyspider"] = {}
                r_copy.request.meta["easyspider"]["from_retry"] = 1
                # 带上item 方便检查错误在哪
                msg = "Error processing %s ; %s" % (json.dumps(item), output.getTraceback())
                spider.put_back_2_start_url(response,
                                            exc_info=msg,
                                            )

        else:
            logkws = self.logformatter.scraped(output, response, spider)
            logger.log(*logformatter_adapter(logkws), extra={'spider': spider})
            # ----Add fingerprint--------
            fp = request_fingerprint(rq)
            try:
                spider.server.sadd("%s:dupefilter" % spider.name, fp)
            except Exception:
                logger.exception("when _itemproc_finished, add into request fingerprint failed....")
            # ------remove request record beacuse successed-----

            # data = self._encode_request_for_remove_successed_request(response.request, spider)
            # spider.server.execute_command("ZREM", '%(spider)s:requests' % {"spider": spider.name}, data)
            # print "\n\nremove .... remove \n\n"
            # print "\n\n request is data %s" % repr(data)
            # --------------------------------------------------

            # ------add successed_urls urls-----
            # ------2018-03-13 13:17:19  不再保存successed_url 会导致redis过大
            # successed_request = spider.parse_request_to_dict(response)
            # try:
            #     spider.server.sadd("%s:successed_urls" % spider.name, json.dumps(successed_request))
            # except Exception:
            #     logger.exception("in _itemproc_finished, add successed request failed....")
            # --------------------------------------------------
            return self.signals.send_catch_log_deferred(
                signal=signals.item_scraped, item=output, response=response,
                spider=spider)

    def _encode_request_for_remove_successed_request(self, request, spider):
        """Encode a request object"""
        obj = request_to_dict(request, spider)
        return picklecompat.dumps(obj)

    def enqueue_scrape(self, response, request, spider):
        """某些极端的情况下，可能scraper本身出错，这个就严重了....需要汇报作者
        一般情况下来说，作为基础组件的scraper，是绝对不会出错的
        """
        slot = self.slot
        dfd = slot.add_response_request(response, request)

        def finish_scraping(_):
            slot.finish_response(response, request)
            self._check_if_closing(spider, slot)
            self._scrape_next(spider, slot)
            return _
        dfd.addBoth(finish_scraping)

        def scraper_bug(f):
            """出现了严重的问题
            """
            r_copy = response.copy()
            # 如果直接从 yiled Reuest 过来的话，那就是没有带上 easyspider 信息的
            if "easyspider" not in r_copy.request.meta:
                r_copy.request.meta["easyspider"] = {"from_retry": 1}
            else:
                r_copy.request.meta["easyspider"]["from_retry"] += 1

            reason = 'Scraper bug processing %(request)s please contact hhczy1003@163.com for help' % {'request': request}
            logger.error(reason, exc_info=failure_to_exc_info(f), extra={'spider': spider})
            # 很有可能就是调用了 blocked_call_back ，然后blocked_call_back 调用了report 无法输出导致错误的，所以这里就直接提交到redis 去，不再处理
            # spider.blocked_call_back(response, reason=reason, exc_info=f.getTraceback())
            spider.put_back_2_start_url(r_copy,
                                        exc_info=u"%s; %s" % (reason, f.getTraceback()),
                                        )

        dfd.addErrback(scraper_bug)
        self._scrape_next(spider, slot)
        return dfd
