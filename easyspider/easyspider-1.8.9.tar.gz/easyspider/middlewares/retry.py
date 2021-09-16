# coding=utf-8
import traceback
import logging
from scrapy_redis import connection
from scrapy.downloadermiddlewares.retry import RetryMiddleware
"""

[当连接超时(代理无效的时候要重试)或者当500错误被屏蔽的时候要重试, 而不是直接报错误而放弃]
"""

logger = logging.getLogger(__name__)


class retryToStartMiddleware(RetryMiddleware):
    """

    [请求失败后被重置是放在队尾，也就是 rpush]
    """

    def __init__(self, settings):
        super(retryToStartMiddleware, self).__init__(settings)
        self.server = connection.from_settings(settings)

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1

        if retries <= self.max_retry_times:
            logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            # retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust
            return retryreq
        else:
            # print "\n\n\n\n\n\n  in else \n\n\n\n"
            logger.debug("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
            # put_back_2_start_url 做了request还是response 的判断...可惜blocked_call_back没有，不然上面的logger也能合并为一条
            # msg = traceback.format_exc(reason)
            msg = traceback.format_exc()
            # easyspider = request.meta.get("easyspider") or {}
            # if not easyspider:
            #     request.meta["easyspider"] = {"from_retry": 1}
            # else:
            #     request.meta["easyspider"]["from_retry"] += 1
            spider.put_back_2_start_url(request, exc_info={
                "request": request.url,
                "traceback": msg,
                "body": None,
            })
