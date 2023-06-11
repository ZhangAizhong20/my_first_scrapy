# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import time
import random

from bs4 import BeautifulSoup
from scrapy.http import HtmlResponse
from scrapy import signals, Selector

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


# from spiders.one_page import OnePageSpider


class FirstTimeSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.
        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class FirstTimeDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called

        # if 'content-autofill.googleapis.com' in request.url:
        #     raise scrapy.exceptions.IgnoreRequest("Blocked by middleware")
        return None

    def process_response(self, request, response, spider):

        # return  response
        # return response
        # Called with the response returned from the downloader.
        # pass
        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        # 响应对象中存储页面数据的篡改
        # print('即将返回一个新的响应对象!!!')
        # #如何获取动态加载出来的数据
        bro = spider.driver
        bro.get(url=request.url)
        time.sleep(0.25)
        page_text = bro.page_source

        soup = BeautifulSoup(page_text, 'html.parser')
        comments = soup.select('#comment_all_content > div > div')
        i = 1
        for comment in comments:
            # comment_all_content > div > div:nth-child(5) > div > div.level2_box > div.level2_list > div.view_more > span
            subcom_number = 0
            try:
                # 判断是否需要点击
                subcom_number = int(
                    comment.select_one('div > div.level2_box > div.level2_list > div.view_more > span').text)
            except:
                subcom_number = 0
            if subcom_number > 0:
                but = bro.find_element("css selector", f"#comment_all_content > div > div:nth-child({i}) > div > div.level2_box > div.level2_list > div.view_more > a")
                but.click()
                time.sleep(0.02)
            i += 1
            time.sleep(0.1)

        page_text = bro.page_source
        return HtmlResponse(url=spider.driver.current_url, body=page_text, encoding='utf-8', request=request)

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class RandomUserAgentMiddleware(object):

    def __init__(self, user_agent_list):
        self.user_agent_list = user_agent_list

    # @classmethod
    # def from_crawler(cls, crawler):
    #     settings = crawler.settings
    #     user_agent_list = settings.get('USER_AGENT_LIST')
    #     return cls(user_agent_list)

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agent_list)
        request.headers.setdefault('User-Agent', user_agent)

    def process_response(self, request, response, spider):
        return response
# 快代理中间键，拦截请求
# 动态爬取建议直接初始化代理
# class ProxyDownloaderMiddleware:
#     _proxy = ('XXX.kdlapi.com', '15818')

#     def process_request(self, request, spider):

#         # 用户名密码认证
#         username = "username"
#         password = "password"
#         request.meta['proxy'] = "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": ':'.join(ProxyDownloaderMiddleware._proxy)}

#         # 白名单认证
#         # request.meta['proxy'] = "http://%(proxy)s/" % {"proxy": proxy}

#         request.headers["Connection"] = "close"
#         return None

#     def process_exception(self, request, exception, spider):
#         """捕获407异常"""
#         if "'status': 407" in exception.__str__():  # 不同版本的exception的写法可能不一样，可以debug出当前版本的exception再修改条件
#             from scrapy.resolver import dnscache
#             dnscache.__delitem__(ProxyDownloaderMiddleware._proxy[0])  # 删除proxy host的dns缓存
#         return exception
