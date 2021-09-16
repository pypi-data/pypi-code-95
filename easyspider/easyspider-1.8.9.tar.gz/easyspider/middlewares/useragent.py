# coding=utf-8

from easyspider.utils.userAgentList import UA_headers
import random


class userAgentMiddleware(object):

    def process_request(self, request, spider):
        this_time_ua = random.choice(UA_headers)
        if this_time_ua:
            request.headers.setdefault(
                "User-Agent", this_time_ua["User-Agent"])
