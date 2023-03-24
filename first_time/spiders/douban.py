import scrapy
from scrapy import Selector
from first_time.items import MovieItem

class DoubanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['movie.douban.com/']
    start_urls = ['https://movie.douban.com/top250']

    def parse(self, response):
        sel = Selector(response)
        list_items = sel.css('#content > div > div.article > ol > li')
        for list_item in list_items:
            movie = MovieItem()
            movie['title'] = list_item.css('span.title::text').extract_first()
            movie['subject'] = list_item.css('span.inq::text').extract_first()
            movie['rank'] = list_item.css('span.rating_num::text').extract_first()#
            yield movie