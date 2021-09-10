# coding=utf-8
from easyspider.spiders.easyCrawlSpider import easyCrawlSpider
from scrapy import Request


class test_redis_cli(easyCrawlSpider):
    
    name = 'baiduSpider_2'

    def start_requests(self):
        for i in xrange(1, 6283 + 1):
            yield Request("http://www.baidu.com/s?wd=%s" % i)

    def parse(self, response):
        print "crawled %s" % response.url
