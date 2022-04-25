# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewparserItem(scrapy.Item):
    name = scrapy.Field()
    link = scrapy.Field()
    authors = scrapy.Field()
    price_old = scrapy.Field()
    price_act = scrapy.Field()
    rating = scrapy.Field()
    _id = scrapy.Field()
