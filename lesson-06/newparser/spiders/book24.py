

import scrapy
from scrapy.http import HtmlResponse
from newparser.items import NewparserItem

class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/%D0%BF%D1%81%D0%B8%D1%85%D0%BE%D0%BB%D0%BE%D0%B3%D0%B8%D1%8F/?stype=0']

    def parse(self, response: HtmlResponse):
        # response.status
        next_page = response.xpath("//a[@class='pagination-next__text']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[@class='product-title-link']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):

        name = response.css("h1::text").get()
        link = response.url
        authors = response.xpath("//a[@data-event-label='author']/text()").get()
        price_old = response.xpath("//div[@class='buying-priceold-val']/span/text()").get()
        price_act = response.xpath("//div[@class='buying-pricenew-val']/span/text()").get()
        rating = response.xpath("//div[@id='rate']/text()").get()

        yield NewparserItem(name=name, link=link, authors=authors, price_old=price_old, price_act=price_act,rating=rating)
