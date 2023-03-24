
import scrapy
from scrapy import Selector,Request
from first_time.items import StockItem
from scrapy.http import HtmlResponse
class StockSpider(scrapy.Spider):
    name = 'stock'
    allowed_domains = ['guba.eastmoney.com/']
    
    def start_requests(self):
        max_page = 10
        stock_number = 600601
        for i in range(1,max_page):
            yield Request(url = f'http://guba.eastmoney.com/list,{stock_number}_{i}.html')
    def parse(self, response:HtmlResponse):
        sel = Selector(response)
        list_items = sel.css('#articlelistnew > div')####articlelistnew > div:nth-child(2),,  /div[2]
        
        for item in list_items:
            stock = StockItem()
            stock['view_number'] = item.css('span.l1.a1::text').get()
            stock['comment_number'] = item.css('span.l2.a2::text').get()#
            # //*[@id="articlelistnew"]/div[2]
            # stock.title = item.css('span.l2.a2::text')
            stock['title'] = item.css('span.l3.a3 > a::attr(title)').get()
            try:
                stock['author'] = item.css('span.l4.a4 > a::attr(href)').get()#articlelistnew > div:nth-child(2) > span.l4.a4 > a
            except:
                stock['author'] = None
            stock['it_url'] = item.css('span.l3.a3 > a::attr(href)').get()
            stock['update'] = item.css('span.l5.a5::text').get()

            if stock['comment_number'] == None or stock['comment_number'] =='阅读':
                continue
            else:
                yield stock
        # for list_item in list_items:
        #     movie = MovieItem()
        #     movie['title'] = list_item.css('span.title::text').extract_first()
        #     movie['subject'] = list_item.css('span.inq::text').extract_first()
        #     movie['rank'] = list_item.css('span.rating_num::text').extract_first()
        #     yield movie
