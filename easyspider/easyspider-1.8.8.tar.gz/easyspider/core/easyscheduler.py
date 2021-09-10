# -*- coding: utf-8 -*-
# @Author: zhangTian
# @Email:  hhczy1003@163.com
# @Date:   2017-07-08 13:48:45
# @Last Modified by:   hang.zhang
# @Last Modified time: 2018-03-18 06:57:22


# TODO: 队列监控反馈
import logging
from scrapy_redis.scheduler import Scheduler
from twisted.internet.threads import deferToThread
logger = logging.getLogger(__name__)


class easyScheduler(Scheduler):

    def has_pending_requests(self):
        """in this method, you should only return True regardless what len(self) is

        because in a extreme case, spider machine may lost connection with the redis
        (ADSL dailing interval or even worse case: the ADSL interface had crush down and must reboot to resume),

        if can not connect to redis, len(self) will casuse Exception, because of the Exception, crawler can not
        run into next_request, and run into a useless loop, never require more request from redis anymore(because next_requsts not called)
        """
        try:
            return len(self) > 0
        except Exception:
            logger.exception("in easyScheduler: check has_pending_requests,  len(self) failed, return false")
            return False

    def enqueue_request(self, request):
        if not request.dont_filter and self.df.request_seen(request):
            self.df.log(request, self.spider)
            return False
        if self.stats:
            self.stats.inc_value('scheduler/enqueued/redis', spider=self.spider)

        return deferToThread(self.defer_push, request)

    def defer_push(self, request):
        # loop until connected to redis
        while True:
            try:
                self.queue.push(request)
                return True
            except Exception:
                logger.exception("in easyScheduler: enqueue_request,  self.queue.push(request) failed, return True %s" % request)
                # 2018-03-18 06:19:52： 暂时想不出好办法，在 掉线的时候怎么办。。。
                # 出现的典型状况是，adsl 掉线的时候，刚好运行到这里，然后就一直卡主，在这里循环，执行权限没有放开
                # 想搞个子进程通信，把adsl独立开，这样即使这里一直被卡住，adsl 到时间了，也能自动恢复，等它恢复了，这里也就好了
                # return True
