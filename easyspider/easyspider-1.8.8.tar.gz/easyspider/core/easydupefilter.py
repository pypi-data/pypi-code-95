# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2017-09-05 16:20:40
# @Last Modified by:   hang.zhang
# @Last Modified time: 2018-03-04 14:02:54

from scrapy_redis.dupefilter import RFPDupeFilter
import logging


logger = logging.getLogger(__name__)


class easyRFPDupeFilter(RFPDupeFilter):

    def request_seen(self, request):
        """
        1. 增加try except 避免在机器断网的时候，无法连接redis避免崩溃结束
        2. 改变 dupefilter插入时间，只有当request能产生结果，才会被加入dupefilter
        (即是否重复的标准，是否请求过，变成是否产生结果)。

        主要是应对以下场景： 如果请求被屏蔽，那么这个请求，就无法获得结果。

        而根据原始的逻辑来看，这个请求你确实已经发出了，并且有响应。那么你这个请求在发出的时候，就已经加入了dupefilter，下次就不会再被调度，【请求就会被丢失】

        这样做的目的，是精细化抓取，严格要求，不丢掉一条请求
        """
        fp = self.request_fingerprint(request)
        # This returns the number of values added, zero if already exists.
        try:
            # added = self.server.sadd(self.key, fp)
            added = self.server.sismember(self.key, fp)
            return added
        except Exception:
            # return false to schedler this request
            logger.exception("in easyRFPDupeFilter: check is in dupefilter failed, return false")
            return False
