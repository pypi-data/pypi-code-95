# coding=utf-8
import logging
from scrapy.exceptions import IgnoreRequest

logger = logging.getLogger(__name__)


class spiderIsAnti(IgnoreRequest):

    def __init__(self, response, *args, **kwargs):
        pass


class antiSpiderMiddleware(object):

    def process_spider_input(self, response, spider):
        # 如果在spider中没有定义isAntiSpider，检测是否被屏蔽的操作，那么就默认都不被屏蔽
        if not hasattr(spider, "is_blocked_spider"):
            return
        # 如果定义了isAntiSpider，那么一般情况下返回False,因为名字是isAntiSpider是否被触发，所以返回False就是没有被触发，返回False就是被触发
        if not spider.is_blocked_spider(response):
            return
        # 如果定义了触发反爬之后的动作，那么就调用这个动作，否则什么都不干
        if hasattr(spider, "blocked_call_back"):
            spider.blocked_call_back(response)
        # 在上面起始已经处理了被屏蔽之后的动作，这里只是记录一下
        raise spiderIsAnti(response)

    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, spiderIsAnti):
            logger.info(
                "Ignoring response %(response)r: Spider is blocked or not allowed",
                {'response': response}, extra={'spider': spider},
            )
            """
                如果返回为None的话，那么其他中间件的process_spider_exceptions会一直被调用，直到所有中间件被调用，该异常到达引擎(异常将被记录或忽略)
                如果返回一个包含response,dict,item的可迭代对象，那么这个中间件的process_spider_output方法会被调用，其他的process_spider_exception　不会被调用
                第二个返回，就相当于正常调用process_spider_output方法
            """
            return []
