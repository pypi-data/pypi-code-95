# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class C103items(scrapy.Item):
    ticker = scrapy.Field()
    title = scrapy.Field()
    df = scrapy.Field()
