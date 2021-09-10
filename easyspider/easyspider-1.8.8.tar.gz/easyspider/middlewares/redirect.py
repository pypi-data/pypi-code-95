# coding=utf-8

import logging
from six.moves.urllib.parse import urljoin
from scrapy.downloadermiddlewares.redirect import BaseRedirectMiddleware

logger = logging.getLogger(__name__)

"""
    目的：让无限多次的302跳转，不会把请求内容丢弃，【还是返回给spider】让spider的【is_anti_spider】来处理

    1. 只是在原来基础上 _redirect　多加了一个response的参数，
    注释了raise IgnoreRequest("max redirections reached") 加了一个return response
    2. 对于循环请求http://www.baidu.com/saa?wd=%s" % i 这个例子来说，由于baidu把出错的全部导向到error页面
    循环请求的时候，第一次之后，其他由于一样的请求，都被filter了，所以在302的时候，应该不管什么情况都要dont_filter
"""


class myBaseRedirectMiddleware(BaseRedirectMiddleware):

    def _redirect(self, redirected, request, spider, reason, response):
        ttl = request.meta.setdefault('redirect_ttl', self.max_redirect_times)
        redirects = request.meta.get('redirect_times', 0) + 1

        if ttl and redirects <= self.max_redirect_times:
            redirected.meta['redirect_times'] = redirects
            redirected.meta['redirect_ttl'] = ttl - 1
            redirected.meta['redirect_urls'] = request.meta.get('redirect_urls', []) + \
                [request.url]
            # 为什么scrapy源码会写出这一行来 ? 这不是开玩笑吗 ？
            # 你request.replace就复制了request还需要做这个操作？坚决注释替换
            # redirected.dont_filter = request.dont_filter
            redirected.priority = request.priority + self.priority_adjust
            logger.debug("Redirecting (%(reason)s) to %(redirected)s from %(request)s",
                         {'reason': reason, 'redirected': redirected, 'request': request})
            return redirected
        else:
            # 原来的操作是raise 错误，现在是提示，并且放回起始队列
            # logger.info("Discarding %(request)s: max redirections reached",
            #             {'request': request}, extra={'spider': spider})
            # raise IgnoreRequest("max redirections reached")
            # in this time, response do not bind with a request
            # AttributeError: 'NoneType' object has no attribute 'url'
            # response.request = copy.deepcopy(request)
            response.request = request.copy()
            spider.report_this_crawl_2_log(response, "Discarding %(request)s: max redirections reached" % {'request': request})
            # spider.blocked_call_back(response, "Discarding %(request)s: max redirections reached" % {'request': request})
            return response


class directReturnRedirectMiddleware(myBaseRedirectMiddleware):
    """Handle redirection of requests based on response status and meta-refresh html tag"""

    def process_response(self, request, response, spider):
        if request.meta.get('dont_redirect', False):
            return response
        if request.method == 'HEAD':
            if response.status in [301, 302, 303, 307] and 'Location' in response.headers.to_unicode_dict():
                redirected_url = urljoin(
                    request.url, response.headers.to_unicode_dict()['location'])
                redirected = request.replace(url=redirected_url)
                # 所有的跳转都应该被 dont_filter 以防因为屏蔽而被跳转到同一个链接而不能被记录
                # redirected = redirected.replace(dont_filter=True)
                return self._redirect(redirected, request, spider, response.status, response)
            else:
                return response

        if response.status in [302, 303] and 'Location' in response.headers.to_unicode_dict():
            redirected_url = urljoin(request.url, response.headers.to_unicode_dict()['location'])
            redirected = self._redirect_request_using_get(
                request, redirected_url)
            # 所有的跳转都应该被 dont_filter 以防因为屏蔽而被跳转到同一个链接而不能被记录
            # redirected = redirected.replace(dont_filter=True)
            return self._redirect(redirected, request, spider, response.status, response)

        if response.status in [301, 307] and 'Location' in response.headers.to_unicode_dict():
            redirected_url = urljoin(request.url, response.headers.to_unicode_dict()['location'])
            redirected = request.replace(url=redirected_url)
            # 所有的跳转都应该被 dont_filter 以防因为屏蔽而被跳转到同一个链接而不能被记录
            # redirected = redirected.replace(dont_filter=True)
            return self._redirect(redirected, request, spider, response.status, response)

        return response
