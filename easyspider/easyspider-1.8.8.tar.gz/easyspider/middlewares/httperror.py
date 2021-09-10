# coding=utf-8

"""
继承原有的进行修改减少代码,原来默认是报告，现在添加进 redis记录
"""
from scrapy.spidermiddlewares.httperror import HttpErrorMiddleware

from scrapy.utils.serialize import ScrapyJSONEncoder
from scrapy.exceptions import IgnoreRequest
from scrapy_redis import connection
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
default_serialize = ScrapyJSONEncoder().encode


class HttpError(IgnoreRequest):
    """A non-200 response was filtered"""

    def __init__(self, response, *args, **kwargs):
        self.response = response
        super(HttpError, self).__init__(*args, **kwargs)


class recordHttpErrorMiddleware(HttpErrorMiddleware):

    def __init__(self, settings):
        super(recordHttpErrorMiddleware, self).__init__(settings)
        # 与原来相比新增
        self.serialize = default_serialize
        self.server = connection.from_settings(settings)

    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, HttpError):
            logger.debug(
                "Ignoring response %(response)r: HTTP status code is not handled or not allowed",
                {'response': response}, extra={'spider': spider},
            )
            # 与原来相比新增
            self.recordFailed(response, spider)
            return []

    def recordFailed(self, response, spider):
        # print "\n\n\nin record file\n\n\n"
        source_start_url = response.meta.get("source_start_url")
        if not source_start_url:
            source_start_url = {
                "url": response.meta.get("redirect_urls")[0] if response.meta.get("redirect_urls") else response.url
            }
        source_start_url.update({
            "now_url": response.url,
            "status": response.status,
            "spider": spider.name,
            "time": datetime.utcnow(),
        })
        logger.info(
            "response %(response)r: HTTP status code is not handled or not allowed, the detail msg are %(detail)s",
            {'response': response, "detail": source_start_url}, extra={'spider': spider},
        )
        data = self.serialize(source_start_url)
        self.server.rpush("%s:failed_urls" % (spider.name), data)
