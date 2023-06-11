import random
import string
import time
import zipfile
import re
from shutil import which

import bs4
import scrapy
# from first_time.items import MovieItem
from bs4 import BeautifulSoup
from scrapy import Request
from scrapy.http import HtmlResponse
from scrapy.selector import Selector
from scrapy_selenium import SeleniumRequest
from seleniumwire import webdriver as web1
from selenium import webdriver

# from selenium import By

from first_time.items import TotalPage, Comment, Subcomment
from first_time.chrome_driver import create_proxyauth_extension
# from first_time.chrome_driver import create_proxyauth_extension2
from first_time.chrome_driver import extract_time, process_sub_comment
from first_time.chrome_driver import get_ip_from_api


class total_page(scrapy.Spider):
    name = '300291'

    @staticmethod
    def clear_str(str_raw):
        for pat in ['\n', ' ', ' ', '\r', '\xa0', '\n\r\n']:
            str_raw.strip(pat)
        return str_raw

    # allowed_domains = ['guba.eastmoney.com']
    # start_urls = ['http://guba.eastmoney.com/list,600895_50.html']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.Stock_id = None
        self.missing = 0
        self.begin_page = None
        self.end_page = None
        self.tunnelhost = None
        self.tunnelport = None
        self.start_time = time.time()
        self.if_sele = False
        self.current_time = 0
        self.time_sleep = 1
        self.pox_id = None
        self.pox_sec = None
        self.proxy_username = None
        self.proxy_password = None
        self.use_password = True
        self.use_ip = True

        chrome_options = webdriver.ChromeOptions()
        if self.use_password:  # 用户名验证设置
            proxyauth_plugin_path = create_proxyauth_extension(
                self.tunnelhost,  # 隧道域名
                tunnelport=self.tunnelport,  # 端口号
                proxy_username=self.proxy_username,  # 用户名
                proxy_password=self.proxy_password)  # 密码
            chrome_options.add_extension(proxyauth_plugin_path)
        if self.use_ip:
            chrome_options.add_argument(f'--proxy-server=http://{self.tunnelhost}:{self.tunnelport}')
        prefs = {"profile.managed_default_content_settings.images": 2}  # 禁止加载图片
        chrome_options.add_experimental_option("prefs", prefs)
        custom_settings = {
            'SELENIUM_DRIVER_NAME': 'chrome',
            'SELENIUM_DRIVER_EXECUTABLE_PATH': which('chromedriver'),
            'SELENIUM_DRIVER_ARGUMENTS': chrome_options.to_capabilities(),
            'SELENIUM_BROWSER_OPTIONS': chrome_options.to_capabilities(),
            'DOWNLOADER_MIDDLEWARES': {
                'scrapy_selenium.SeleniumMiddleware': 800,
            },
            'DOWNLOAD_DELAY': 0,  # 关闭默认的下载延迟
        }

        self.header = {"Connection": "close"}

        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def start_requests(self):
       
        '''
        设置起始页码和结束页码
        '''
        begin_page = self.begin_page
        max_page = self.end_page

        
        stock_id = self.Stock_id
        current_id = stock_id
        for i in range(begin_page, max_page + 1):
            
            yield Request(
                url='https://guba.eastmoney.com/list,{}_{}.html'.format(current_id, i),
                headers=self.header,
                callback=self.list_info,
                cb_kwargs={'stock_id': current_id, 'current_page': i},
            )


    def parse(self, response: HtmlResponse, **kwargs):
        pass
        
    def list_info(self, response: HtmlResponse, **kwargs):

        sel = Selector(response)
        list_items = sel.css('#articlelistnew > div')  ####articlelistnew > div:nth-child(2),,  /div[2]
        for item in list_items:

            stock = TotalPage()
            # stock['total_page_number'] = kwargs['total_page_number']
            stock['comments'] = []
            current_page = kwargs['current_page']
            stock['current_page'] = current_page

            stock_id = kwargs['stock_id']
            stock['stock_id'] = stock_id
            stock['view_number'] = item.css('span.l1.a1::text').get()
            stock['comment_number'] = item.css('span.l2.a2::text').get()  #
            
            stock['title'] = item.css('span.l3.a3 > a::attr(title)').get()
            stock['author'] = item.css(
                'span.l4.a4 > a::text').get()  
            current_url = item.css(
                'span.l3.a3 > a::attr(href)').get()  
            stock['it_url'] = current_url
            # print(current_url)
            stock['update_time'] = item.css('span.l5.a5::text').get()

            if (current_url
                    # and (random.random() < 0.5)   #取消注释则一个页面随机爬取30%的帖子
            ):

                # caifuhao爬取方式和普通帖子方式不同，需要注意
                if 'caifuhao' in current_url:
                    url = 'https:' + current_url
                    print(url)
                    yield Request(url=url, callback=self.caifuhao_full_page, cb_kwargs={'stock': stock},
                                  headers=self.header,

                                  )

                elif '/new' in current_url:
                    yield Request(url='http://guba.eastmoney.com{}'.format(current_url),
                                  callback=self.norm_full_page,
                                  cb_kwargs={'stock': stock},
                                  headers=self.header,
                                  # wait_time=self.time_sleep
                                  )
                else:
                    continue
            else:
                continue

    def norm_full_page(self, response: HtmlResponse, **kwargs):

        

        sel = Selector(response)
        html = response.text  # 将网页源码转换格式为html
        soup = BeautifulSoup(html, features="lxml")
        stock = kwargs['stock']  # zwconttb > div.zwfbtime > span
        # print(html)
        stock['maintext'] = self.clear_str(soup.find('div', {'id': 'post_content'}).text)
        # stock['author'] = sel.css(
        stock['author_ip'] = sel.css(
            '#line2 > div.post_author_info.fl.cl > span.post_ip.fl::text').extract_first()  # zwconttb > div.zwfbtime > span
        stock['publish_time'] = sel.css('#line2 > div.post_author_info.fl.cl > span.post_time.fl::text').extract_first()
        # 换ip
        if (stock['maintext']) and (stock['author_ip'] is None):
            stock['author_ip'] = sel.css('#zwconttb > div.zwfbtime > span::text').get()
            stock['publish_time'] = extract_time(
                sel.css('#zwconttb > div.zwfbtime::text').get())  # zwconttb > div.zwfbtime
            self.missing += 1
        com_page = 1
        try:
            com_page = int(sel.css(
                '#newspage > span > span:nth-child(1) > span::text').get())  # newspage > span > span:nth-child(1) > span
        except:
            pass

        if 1 < com_page:
            # newspage > span > span:nth-child(1) > a.on
            # newspage > span > span:nth-child(1) > a:nth-child(3)
            target_page = 1

            target_url = sel.css(
                f'#newspage > span > span:nth-child(1) > a:nth-child({target_page + 1})::attr(href)').get()  # newspage > span > span:nth-child(1) > a:nth-child(4)
            # newspage > span > span:nth-child(1) > a:nth-child(3)
            yield Request(url='https://guba.eastmoney.com{}'.format(target_url), callback=self.norm_comment,
                          cb_kwargs={'stock': stock, 'current_page': target_page, 'total_page': com_page},
                          headers=self.header,
                          # wait_time=self.time_sleep
                          )
        # 没有更多评论
        else:
            comment_list = sel.css(
                '#comment_all_content > div > div')  # comment_all_content > div > div:nth-child(1) > div
            i = 1
            for comment in comment_list:
                com = Comment()
                com['author'] = comment.css('div.replyer_info > a::text').get()
                com['time'] = comment.css(
                    'div > div.publish_time > span:nth-child(1)::text').get()  # comment_all_content > div > div:nth-child(1) > div > div.publish_time > span:nth-child(1)
                try:
                    com['likes'] = comment.css(
                        'div > div.news_reply_btns.clearfix > div > span.level1_rebtn.replylike.unlike > span::text').get()
                except:
                    pass

                com['author_location'] = comment.css(
                    'div > div.publish_time > span:nth-child(2)::text').get()  # comment_all_content > div > div:nth-child(4) > div > div.publish_time > span:nth-child(2)
                com['text'] = comment.css(
                    'div > div.level1_reply_cont > div.short_text::text').get()  # comment_all_content > div > div:nth-child(1) > div > div.level1_reply_cont > div.short_text
                com['subcomments'] = []

                # 开始处理2级评论
                subcomments = comment.css(
                    'div > div.level2_box > div.level2_list > div.level2_item.previewL2')  # div > div.level2_box > div.level2_list > div.level2_item.previewL2
                if len(subcomments) == 0:
                    subcomments = comment.css(
                        'div > div.level2_box > div.level2_list > div.level2_item.viewmoreL2')
                for subcomment in subcomments:
                    com['subcomments'].append(dict(process_sub_comment(subcomment)))

                # try:
                #     subcom_page = int(comment.css(
                #         'div > div.level2_box > div.level2_list > div.sreply_pager > span > span > span::text').get())
                # except:
                #     subcom_page = 0
                # if subcom_page > 1:
                #     for p in range(2, subcom_page + 1):
                #         posi = f'#comment_all_content > div > div:nth-child({i}) > div > div.level2_box > div.level2_list > div.sreply_pager > span > span > a[data-page="{p}"]'
                #         but = self.driver.find_element("css selector", posi)
                #         but.click()
                #         subcomment_page = self.driver.page_source
                #         subcom_soup = BeautifulSoup(subcomment_page, 'html.parser')
                #         subcomments = subcom_soup.select(
                #             f'#comment_all_content > div > div:nth-child({i}) > div > div.level2_box > div.level2_list > div.level2_item.viewmoreL2')
                #         for subcomment in subcomments:
                #             com['subcomments'].append(dict(process_sub_comment(subcomment)))

                stock['comments'].append(dict(com))
                i += 1
            print('readytoyield')
            yield stock

    def norm_comment(self, response: HtmlResponse, **kwargs):
        i = 1
        sel = Selector(response)
        current_page = kwargs[
            'current_page']  # comment_all_content > div > div:nth-child(1) > div > div.level1_reply_cont > div.short_text
        stock = kwargs['stock']
        total_page_number = kwargs['total_page']
        comment_list = sel.css(
            '#comment_all_content > div > div')  # comment_all_content > div > div:nth-child(25) > div > div.level1_reply_cont > div.short_text
        for comment in comment_list:  # comment_all_content > div > div:nth-child(1)
            com = Comment()
            com['subcomments'] = []
            com['author'] = comment.css('div.replyer_info > a::text').get()
            com['time'] = comment.css(
                'div > div.publish_time > span:nth-child(1)::text').get()  # comment_all_content > div > div:nth-child(1) > div > div.publish_time > span:nth-child(1)
            try:
                com['likes'] = comment.css(
                    'div > div.news_reply_btns.clearfix > div > span.level1_rebtn.replylike.unlike > span::text').get()
            except:
                pass

            com['author_location'] = comment.css(
                'div > div.publish_time > span:nth-child(2)::text').get()  # comment_all_content > div > div:nth-child(25) > div > div.publish_time > span:nth-child(2)
            com['text'] = comment.css(
                'div > div.level1_reply_cont > div.short_text::text').get()  # div > div.level1_reply_cont > div.short_text
            subcomments = comment.css(
                'div > div.level2_box > div.level2_list > div.level2_item.previewL2')  # div > div.level2_box > div.level2_list > div.level2_item.previewL2
            if len(subcomments) == 0:
                subcomments = comment.css(
                    'div > div.level2_box > div.level2_list > div.level2_item.viewmoreL2')
            for subcomment in subcomments:
                com['subcomments'].append(dict(process_sub_comment(subcomment)))

            # try:
            #     subcom_page = int(comment.css(
            #         'div > div.level2_box > div.level2_list > div.sreply_pager > span > span > span::text').get())
            # except:
            #     subcom_page = 0
            # if subcom_page > 1:
            #     for p in range(2, subcom_page + 1):
            #         posi = f'#comment_all_content > div > div:nth-child({i}) > div > div.level2_box > div.level2_list > div.sreply_pager > span > span > a[data-page="{p}"]'
            #         but = self.driver.find_element("css selector", posi)
            #         but.click()
            #         subcomment_page = self.driver.page_source
            #         subcom_soup = BeautifulSoup(subcomment_page, 'html.parser')
            #         subcomments = subcom_soup.select(
            #             f'#comment_all_content > div > div:nth-child({i}) > div > div.level2_box > div.level2_list > div.level2_item.viewmoreL2')
            #         for subcomment in subcomments:
            #             com['subcomments'].append(dict(process_sub_comment(subcomment)))

            stock['comments'].append(dict(com))
            i += 1

        if current_page < total_page_number:
            target_page = current_page + 1
            target_url = sel.css(
                f'#newspage > span > span:nth-child(1) > a[data-page="{target_page}"]::attr(href)').get()

            yield Request(url='https://guba.eastmoney.com{}'.format(target_url), callback=self.norm_comment,
                          cb_kwargs={'stock': stock, 'current_page': target_page,
                                     'total_page': total_page_number},
                          headers=self.header,
                          # wait_time=self.time_sleep
                          )
            print('success yield request')

        else:
            yield stock
        # cb_kwargs={'stock':stock,'current_page':target_page,'total_page':com_page}    

    def caifuhao_full_page(self, response: HtmlResponse, **kwargs):

        sel = Selector(response)
        html = response.text  # 将网页源码转换格式为html
        soup = BeautifulSoup(html, features="lxml")
        stock = kwargs['stock']
        # print(html)
        try:
            stock['maintext'] = soup.find('div', 'article-body').get_text()
        except:
            stock['maintext'] = 'nothing'
        stock['author'] = sel.css(
            '#main > div.grid_wrapper > div.grid > div.g_content > div.article.page-article > div.article-head > '
            'div.article-meta > span.item > a::text').extract_first()
        stock['author_ip'] = sel.css(
            '#main > div.grid_wrapper > div.grid > div.g_content > div.article.page-article > div.article-head > '
            'div.article-meta > span:nth-child(3)::text').extract_first()
        stock['publish_time'] = sel.css(
            '#main > div.grid_wrapper > div.grid > div.g_content > div.article.page-article > div.article-head > '
            'div.article-meta > span:nth-child(2)::text').extract_first()

        # 发现更多评论的url继续调用
        current_url2 = None
        try:
            current_url2 = sel.css('#comment_all > div.bottom_btns.clearfix > a::attr(href)').get()
        except:
            current_url2 = None

        if current_url2:
            print(current_url2)
            url = 'https:' + current_url2
            yield Request(url=url, cb_kwargs={'stock': stock, 'current_page': 1},
                          callback=self.caifuhao_comment,
                          headers=self.header,
                          # wait_time=self.time_sleep
                          )

        # 没发现就算了呗
        else:
            comment_list = sel.css('#comment_all_content > div > div')
            i = 1
            for comment in comment_list:
                com = Comment()
                if com['author'] is None:
                    com['author'] = comment.css('div > div.replyer_info.clearfix > div.userbox.fl > a::text').get()
                com['time'] = comment.css(
                    'div > div.publish_time > span:nth-child(1)::text').get()
                try:
                    com['likes'] = comment.css(
                        'div > div.news_reply_btns.clearfix > div > span.level1_rebtn.replylike.unlike > span::text').get()
                except:
                    pass

                com['author_location'] = comment.css(
                    'div > div.publish_time > span:nth-child(2)::text').get()  # comment_all_content > div > div:nth-child(4) > div > div.publish_time > span:nth-child(2)
                com['text'] = comment.css(
                    'div > div.level1_reply_cont > div.short_text::text').get()  # comment_all_content > div > div:nth-child(1) > div > div.level1_reply_cont > div.short_text
                com['subcomments'] = []
                subcomments = comment.css(
                    'div > div.level2_box > div.level2_list > div.level2_item.previewL2')  # div > div.level2_box > div.level2_list > div.level2_item.previewL2
                if len(subcomments) == 0:
                    subcomments = comment.css(
                        'div > div.level2_box > div.level2_list > div.level2_item.viewmoreL2')
                for subcomment in subcomments:
                    com['subcomments'].append(dict(process_sub_comment(subcomment)))
                #
                # try:
                #     subcom_page = int(comment.css(
                #         'div > div.level2_box > div.level2_list > div.sreply_pager > span > span > span::text').get())
                # except:
                #     subcom_page = 0
                # if subcom_page > 1:
                #     for p in range(2, subcom_page + 1):
                #         posi = f'#comment_all_content > div > div:nth-child({i}) > div > div.level2_box > div.level2_list > div.sreply_pager > span > span > a[data-page="{p}"]'
                #         but = self.driver.find_element("css selector", posi)
                #         but.click()
                #         subcomment_page = self.driver.page_source
                #         subcom_soup = BeautifulSoup(subcomment_page, 'html.parser')
                #         subcomments = subcom_soup.select(
                #             f'#comment_all_content > div > div:nth-child({i}) > div > div.level2_box > div.level2_list > div.level2_item.viewmoreL2')
                #         for subcomment in subcomments:
                #             com['subcomments'].append(dict(process_sub_comment(subcomment)))

                stock['comments'].append(dict(com))
                i += 1

            yield stock

    def caifuhao_comment(self, response: HtmlResponse, **kwargs):

        stock = kwargs['stock']
        current_page = kwargs['current_page']
        sel = Selector(response)
        comments = sel.css('#comment_all_content > div > div')
        i = 1
        for comment in comments:
            com = Comment()
            com['subcomments'] = []
            com['author'] = comment.css('div > div.replyer_info > a::text').get()
            com['time'] = comment.css('div > div.publish_time > span:nth-child(1)::text').get()
            com['likes'] = comment.css(
                'div > div.news_reply_btns.clearfix > div > span.level1_rebtn.replylike.unlike > span::text').get()
            com['author_location'] = comment.css(
                'div > div.publish_time > span:nth-child(2)::text').get()  # comment_all_content > div > div:nth-child(10) > div > div.publish_time > span:nth-child(2)
            com['text'] = comment.css(
                'div > div.level1_reply_cont > div.short_text::text').get()  # > div > div.level1_reply_cont > div.short_text

            # comment_all_content > div > div:nth-child(10) > div > div.level2_box > div.level2_list > div:nth-child(1)
            subcomments = comment.css(
                'div > div.level2_box > div.level2_list > div.level2_item.previewL2')  # div > div.level2_box > div.level2_list > div.level2_item.previewL2
            if len(subcomments) == 0:
                subcomments = comment.css(
                    'div > div.level2_box > div.level2_list > div.level2_item.viewmoreL2')
            for subcomment in subcomments:
                com['subcomments'].append(dict(process_sub_comment(subcomment)))

            stock['comments'].append(dict(com))
            # try:
            #     subcom_page = int(comment.css(
            #         'div > div.level2_box > div.level2_list > div.sreply_pager > span > span > span::text').get())
            # except:
            #     subcom_page = 0
            # if subcom_page > 1:
            #     for p in range(2, subcom_page + 1):
            #         posi = f'#comment_all_content > div > div:nth-child({i}) > div > div.level2_box > div.level2_list > div.sreply_pager > span > span > a[data-page="{p}"]'
            #         but = self.driver.find_element("css selector", posi)
            #         but.click()
            #         subcomment_page = self.driver.page_source
            #         subcom_soup = BeautifulSoup(subcomment_page, 'html.parser')
            #         subcomments = subcom_soup.select(
            #             f'#comment_all_content > div > div:nth-child({i}) > div > div.level2_box > div.level2_list > div.level2_item.viewmoreL2')
            #         for subcomment in subcomments:
            #             com['subcomments'].append(dict(process_sub_comment(subcomment)))
            #

            # i += 1
        # 判断一共有几页，没找到就说明只有一个页码
        # 加入subcomment
        # comment_all_content > div > div:nth-child(14) > div > div.level2_box > div.level2_list > div.sreply_pager > span > span > span
        try:
            total_comment_page = int(sel.css(
                '#newspage > span > span:nth-child(1) > span::text').get())  # newspage > span > span:nth-child(1) > a:nth-child(3)

        except:
            total_comment_page = 1

        if current_page < total_comment_page:
            target_page = current_page + 1
            target_url = sel.css(
                f'#newspage > span > span:nth-child(1) > a[data-page="{target_page}"]::attr(href)').get()

            yield Request(url='https://guba.eastmoney.com{}'.format(target_url), callback=self.caifuhao_comment,
                          cb_kwargs={'stock': stock, 'current_page': target_page},
                          headers=self.header,
                          # wait_time=self.time_sleep
                          )
        else:
            yield stock

    def closed(self, response):
        self.driver.quit()


class Zazesus1(total_page):
    name = 'run1'

    def __init__(self, arg1=None, arg2=None, arg3=None, **kwargs):
        self.Stock_id = str(arg3)
        self.missing = 0
        self.begin_page = int(arg1)
        self.end_page = int(arg2)
        self.tunnelhost = "x406.kdltps.com"
        self.tunnelport = "15818"
        self.start_time = time.time()
        self.if_sele = False
        self.time_sleep = 2
        self.proxy_username = "XXXX"
        self.proxy_password = "XXXX"
        self.pox_id = 'XXXX'
        self.pox_sec = 'XXXX'
        self.use_password = True
        self.use_ip = True

        self.header = {"Connection": "close"}
        custom_settings = {
            'JOBDIR': f'../jobs/{arg3}_{arg1}',
        }
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2,
                 "profile.password_manager_enabled": False,
                 "credentials_enable_service": False,
                 "password_manager_enabled": False,
                 '--disable-features=AutofillEnable': False}
        chrome_options.add_experimental_option("prefs", prefs)
        if self.use_password:  # 用户名验证设置
            proxyauth_plugin_path = create_proxyauth_extension(
                self.tunnelhost,  # 隧道域名
                tunnelport=self.tunnelport,  # 端口号
                proxy_username=self.proxy_username,  # 用户名
                proxy_password=self.proxy_password)  # 密码
            chrome_options.add_extension(proxyauth_plugin_path)
        if self.use_ip:
            chrome_options.add_argument(f'--proxy-server=http://{self.tunnelhost}:{self.tunnelport}')
        chrome_options.add_experimental_option("prefs", prefs)
        self.header = {"Connection": "close"}
        self.driver = webdriver.Chrome(chrome_options=chrome_options)





