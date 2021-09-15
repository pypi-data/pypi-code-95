import numpy as np
import scrapy
from crawler.scrapymims import OpItem

# To execute the spider
# scrapy crawl images -a urls="https://scrapy.org/community/, https://scrapy.org/"

class ImagesSpider(scrapy.Spider):

    name = "images"

    def __init__(self, *args, **kwargs):
        urls = kwargs.get('urls', [])
        self.start_urls = urls

        print("URL ***********************")
        print(self.start_urls)

        self.logger.info(self.start_urls)
        self.urls_child = []
        super(ImagesSpider, self).__init__(*args, **kwargs)
        print("I ENTERED HERE IN THE CONSTRUCTOR !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    def start_requests(self):

        for url in self.start_urls:

            yield scrapy.Request(url=url, callback=self.parse, dont_filter = True)


    def parse(self, response, dont_filter=False):
        """
        Parse a url and its descendents urls to extract their images urls

        :param response: Object
            An HTTP response

        :param dont_filter: Bool
            Indicates whether this request should not be filtered by the scheduler or not.
            This is used when you want to perform an identical request multiple times
            to ignore the duplicates.
        :return: List of Item object
            Each item represents the url of the page and its images urls
        """

        # first layer crawling
        yield self.parse_deeper(response)

        # second layer crawling
        self.urls_child = response.css('a[href*=http]::attr(href)').getall()

        for url in self.urls_child:

            yield scrapy.Request(url=url, callback=self.parse_deeper, dont_filter = False)


    def parse_deeper(self, response):
        """
        Parse the url to extract images urls
        :param response: Object
            An HTTP response
        :return: Item
            An image item has two fields
            url: string
                the url of the page
            images_url: list of string
                the list of urls of all images within the page
        """

        item = OpItem()

        item["url"] = response.url

        imgs = np.asarray(response.css('img').xpath('@src').getall())

        item['images_url'] = item.extract_clean_imgs(imgs)

        if item.extract_clean_imgs(imgs) is not None:

            return item



# Show the status of jobs, assign id  ... using curl ! using scrapyd

# then use the parallelism on multiple threads and multicores
# then try check how to output status of jobs done and jobs in progress

