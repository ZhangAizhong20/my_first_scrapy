import scrapy
from scrapy import Selector
# from first_time.items import MovieItem
from bs4 import BeautifulSoup
import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.http import HtmlResponse





class WangyiSpider(scrapy.Spider):
    name = 'wangyi'
    #allowed_domains = ['www.xxxx.com']
    start_urls = ['https://news.163.com']
    def __init__(self):
        #实例化一个浏览器对象(实例化一次)
        self.bro = webdriver.Chrome(executable_path='/Users/bobo/Desktop/chromedriver')

    #必须在整个爬虫结束后，关闭浏览器
    def closed(self,spider):
        print('爬虫结束')
        self.bro.quit()
