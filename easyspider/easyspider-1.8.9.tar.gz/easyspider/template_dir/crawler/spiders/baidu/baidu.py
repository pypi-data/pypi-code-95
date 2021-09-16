# coding=utf-8
from easyspider.spiders.easyCrawlSpider import easyCrawlSpider
import urllib
import re
import json
import copy


class baiduSpider(easyCrawlSpider):

    name = 'baiduSpider'

    def start_requests(self):
        """you can add to redis queue or directly yield scrapy.Request to launch request(s)
        del start queue in redis: del baiduSpider:start_urls baiduSpider:dupefilter
        """
        template_start_urls_type = {
            "url": "",                  # Requirement
            "method": "GET",            # optional
            "headers": "",              # optional
            "post_data": {},            # optional, dict or urlencode str
            "cookies": "",              # optional
            "easyspider": {             # optional, easyspider's remark info
                # optional, to mark if this start_url is reloaded from retry
                # middleware
                "from_retry": 0,
                # optional, to mark request's original url, it is useful when
                # multi redirect happend.
                "source_start_url": "",
                "start_url_remark": "easyspider's test module"  # request's remark message
            }
        }
        # add request to redis task queue, search in baidu 'A' -> 'Z'
        search_template_url = "https://www.baidu.com/s?wd=%s"
        search_keyword_alphabet = [chr(i)
                                   for i in xrange(ord("A"), ord("Z") + 1)]

        for keyword in search_keyword_alphabet:
            # attention, use deep copy
            start_info = copy.deepcopy(template_start_urls_type)
            start_info.update({
                "url": search_template_url % keyword
            })
            self.server.rpush("%s:start_urls" % (self.name),
                              json.dumps(start_info, ensure_ascii=False))

    def parse(self, response):

        if not hasattr(self, "rex_extract_keyword"):
            self.rex_extract_keyword = re.compile("(wd=(.*?)&|wd=(.*?)$)")

        search_url = str(response.url)
        search_keyword = urllib.unquote((self.rex_extract_keyword.findall(
            search_url)[0][1] or self.rex_extract_keyword.findall(search_url)[0][2]))
        page = ";".join(response.xpath(
            "//span[@class='fk fk_cur']/../span[2]/text()").extract())

        for div in response.xpath("//div[@class='result c-container ']"):
            title = ";".join(div.xpath("h3/a/text()").extract())
            href = ";".join(div.xpath("h3/a/@href").extract())
            desc = ";".join(div.xpath("div[1]//text()").extract())
            yield {
                "search_url": search_url,
                "search_keyword": search_keyword,
                "page": page,
                "title": title,
                "href": href,
                "desc": desc,
            }
