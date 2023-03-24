import random
import string
import zipfile

import scrapy
# from first_time.items import MovieItem
from bs4 import BeautifulSoup
from scrapy import Request
from scrapy.http import HtmlResponse
from scrapy.selector import Selector
# from seleniumwire import webdriver
from selenium import webdriver

from first_time.items import TotalPage, Comment
from first_time.chrome_driver import create_proxyauth_extension


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
        self.begin_page = None
        self.end_page = None
        self.tunnelhost = None
        self.tunnelport = None
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
        self.header = {"Connection": "close"}
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def start_requests(self):
        # sel = Selector(response)
        # total_page_number = int(sel.css(
        #     '#articlelistnew > div.pager > span > span > span:nth-child(1) > a.last_page::attr(data-page)').get())
        '''
        设置起始页码和结束页码
        '''
        begin_page = self.begin_page
        max_page = self.end_page

        # if total_page_number<=50:
        #     max_page = total_page_number
        # else:
        #     max_page = max(int(total_page_number*0.04),50)
        stock_id = self.Stock_id
        current_id = stock_id
        for i in range(begin_page, max_page + 1):
            yield Request(url='https://guba.eastmoney.com/list,{}_{}.html'.format(current_id, i),
                          headers=self.header,
                          callback=self.list_info,
                          cb_kwargs={
                              # 'total_page_number': total_page_number,
                              'stock_id': current_id, 'current_page': i})

    def parse(self, response: HtmlResponse, **kwargs):
        pass
        # 本来这里想通过页码总数来自动设定爬取多少页，但发现很不科学，建议手动设定
        # 确定爬取页码
        # sel = Selector(response)
        # total_page_number = int(sel.css(
        #     '#articlelistnew > div.pager > span > span > span:nth-child(1) > a.last_page::attr(data-page)').get())
        # max_page = 30
        # begin_page = 20
        # # if total_page_number<=50:
        # #     max_page = total_page_number
        # # else:
        # #     max_page = max(int(total_page_number*0.04),50)
        # current_id = kwargs['stock_id']
        #
        # for i in range(begin_page, max_page + 1):
        #     yield Request(url='https://guba.eastmoney.com/list,{}_{}.html'.format(current_id, i),
        #                   headers=self.header,
        #                   callback=self.list_info,
        #                   cb_kwargs={'total_page_number': total_page_number, 'stock_id': current_id, 'current_page': i})

    def list_info(self, response: HtmlResponse, **kwargs):

        sel = Selector(response)
        list_items = sel.css('#articlelistnew > div')  ####articlelistnew > div:nth-child(2),,  /div[2]
        for item in list_items:

            # 测试代码
            # stock = TotalPage()
            # stock['total_page_number'] = kwargs['total_page_number']
            # stock['comments'] = []
            # current_page = kwargs['current_page']
            # stock['current_page']= current_page

            # stock_id = kwargs['stock_id']
            # stock['stock_id']  = stock_id
            # test_url = 'https://caifuhao.eastmoney.com/news/20230320122316077523690?from=guba&name=5LiJ5YWt6Zu25ZCn&gubaurl=aHR0cDovL2d1YmEuZWFzdG1vbmV5LmNvbS9saXN0LDYwMTM2MC5odG1s'
            # yield Request(url =test_url ,callback=self.caifuhao_full_page,cb_kwargs={'stock':stock})
            ########测试结束

            stock = TotalPage()
            # stock['total_page_number'] = kwargs['total_page_number']
            stock['comments'] = []
            current_page = kwargs['current_page']
            stock['current_page'] = current_page

            stock_id = kwargs['stock_id']
            stock['stock_id'] = stock_id
            stock['view_number'] = item.css('span.l1.a1::text').get()
            stock['comment_number'] = item.css('span.l2.a2::text').get()  #
            # //*[@id="articlelistnew"]/div[2]
            # stock.title = item.css('span.l2.a2::text')
            stock['title'] = item.css('span.l3.a3 > a::attr(title)').get()
            stock['author'] = item.css('span.l4.a4 > a::text').get()
            current_url = item.css(
                'span.l3.a3 > a::attr(href)').get()  # articlelistnew > div:nth-child(2) > span.l3.a3 > a
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
                                  headers=self.header
                                  )



                elif '/new' in current_url:
                    yield Request(url='http://guba.eastmoney.com{}'.format(current_url), callback=self.norm_full_page,
                                  cb_kwargs={'stock': stock},
                                  headers=self.header
                                  )

                else:
                    continue
            else:
                continue

    def norm_full_page(self, response: HtmlResponse, **kwargs):

        sel = Selector(response)
        html = response.text  # 将网页源码转换格式为html
        soup = BeautifulSoup(html, features="lxml")
        stock = kwargs['stock']
        # print(html)
        stock['maintext'] = self.clear_str(soup.find('div', {'id': 'post_content'}).text)
        stock['author'] = sel.css(
            '#line2 > div.post_author_info.fl.cl > span.author_name.fl > strong > a > font::text').extract_first()  # line2 > div.post_author_info.fl.cl > span.author_name.fl > strong > a > font
        stock['author_ip'] = sel.css('#line2 > div.post_author_info.fl.cl > span.post_ip.fl::text').extract_first()
        stock['publish_time'] = sel.css('#line2 > div.post_author_info.fl.cl > span.post_time.fl::text').extract_first()
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
                          headers=self.header
                          )

        else:
            comment_list = sel.css(
                '#comment_all_content > div > div')  # comment_all_content > div > div:nth-child(1) > div

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
                stock['comments'].append(dict(com))
                # stock.add_comment(com)
            # newspage > span > span:nth-child(1) > a.on
            # newspage > span > span:nth-child(1) > a:nth-child(8)
            # newspage > span > span:nth-child(1) > a:nth-child(7)
            # 二级评论
            # subcomments = comment.css('div > div.level2_box > div.level2_list > div')#comment_all_content > div > div:nth-child(1) > div > div.level2_box > div.level2_list
            # for subcomment in subcomments:
            #     subcom = Subcomment()
            #     try:

            #         subcom['author'] = subcomment.css('div.row1 > span.replyer > a::text').get()
            #         subcom['text'] = subcomment.css('div.row1 > span.span.l2_short_text::text').get()#comment_all_content > div > div:nth-child(13) > div > div.level2_box > div.level2_list > div.level2_item.previewL2 > div.row1 > span.l2_short_text
            #         subcom['time'] = subcomment.css('div.row2.clearfix > span.time.fl::text').get()
            #         subcom['author_location'] = subcomment.css('div.row2.clearfix > span.reply_ip::text').get()

            # newspage > span > span:nth-child(1) > a:nth-child(10)

            #         subcom['likes'] = subcomment.css('div.row2.clearfix > div > span.level2_rebtn.replylike.haslike > span::text').get()#comment_all_content > div > div:nth-child(14) > div > div.news_reply_btns.clearfix > div > span.level1_rebtn.replylike.unlike > span

            #     except:break
            #     comment.add_subcomment(subcomment)
            #     print('success')
            #     print(subcom)

            print('readytoyield')
            yield stock

    def norm_comment(self, response: HtmlResponse, **kwargs):
        sel = Selector(response)
        current_page = kwargs[
            'current_page']  # comment_all_content > div > div:nth-child(1) > div > div.level1_reply_cont > div.short_text
        stock = kwargs['stock']
        total_page_number = kwargs['total_page']
        comment_list = sel.css(
            '#comment_all_content > div > div')  # comment_all_content > div > div:nth-child(25) > div > div.level1_reply_cont > div.short_text
        for comment in comment_list:  # comment_all_content > div > div:nth-child(1)
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
                'div > div.publish_time > span:nth-child(2)::text').get()  # comment_all_content > div > div:nth-child(25) > div > div.publish_time > span:nth-child(2)
            com['text'] = comment.css(
                'div > div.level1_reply_cont > div.short_text::text').get()  # div > div.level1_reply_cont > div.short_text
            stock['comments'].append(dict(com))
            print('success add one comment')

        if current_page < total_page_number:
            target_page = current_page + 1
            target_url = sel.css(
                f'#newspage > span > span:nth-child(1) > a[data-page="{target_page}"]::attr(href)').get()

            yield Request(url='https://guba.eastmoney.com{}'.format(target_url), callback=self.norm_comment,
                          cb_kwargs={'stock': stock, 'current_page': target_page, 'total_page': total_page_number},
                          headers=self.header)
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
            'div.article-meta > span.item > a::text').extract_first()  # authorwrap > a
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
            yield Request(url=url, cb_kwargs={'stock': stock, 'current_page': 1}, callback=self.caifuhao_comment,
                          headers=self.header
                          )

        # 没发现就算了呗
        else:
            comment_list = sel.css(
                '#comment_all_content > div > div')  # comment_all_content > div > div:nth-child(1) > div > div.replyer_info.clearfix > div.userbox.fl > a

            # current_page['comment'] = sel.css('#comment_all_content > div > div:nth-child(3) > div > div.level1_reply_cont > div.full_text::text').get()#comment_all_content > div > div:nth-child(3) > div > div.level1_reply_cont > div.full_text

            for comment in comment_list:
                com = Comment()
                com['author'] = comment.css('div > div.replyer_info.clearfix > div.userbox.fl > a::text').get()
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
                stock['comments'].append(dict(com))
                # stock.add_comment(com)
                # print('success_comment'*2)
            yield stock

    # comment_all_content > div > div:nth-child(18) > div > div.level2_box > div.level2_list > div.level2_item.previewL2 > div.row1 > span.l2_short_text
    # comment_all_content > div > div:nth-child(19) > div > div.level2_box > div.level2_list > div:nth-child(1) > div.row1 > span.l2_full_text
    def caifuhao_comment(self, response: HtmlResponse, **kwargs):
        stock = kwargs['stock']
        current_page = kwargs['current_page']
        sel = Selector(response)
        comments = sel.css('#comment_all_content > div > div')

        for comment in comments:
            com = Comment()
            com['author'] = sel.css('div > div.replyer_info > a::text').get()
            com['time'] = comment.css('div > div.publish_time > span:nth-child(1)::text').get()
            com['likes'] = comment.css(
                'div > div.news_reply_btns.clearfix > div > span.level1_rebtn.replylike.unlike > span::text').get()
            com['author_location'] = comment.css(
                'div > div.publish_time > span:nth-child(2)::text').get()  # comment_all_content > div > div:nth-child(10) > div > div.publish_time > span:nth-child(2)
            com['text'] = comment.css(
                'div > div.level1_reply_cont > div.short_text::text').get()  # > div > div.level1_reply_cont > div.short_text
            # stock.add_comment(com)
            stock['comments'].append(dict(com))
        # 判断一共有几页，没找到就说明只有一个页码

        try:
            total_comment_page = int(sel.css(
                '#newspage > span > span:nth-child(1) > span::text').get())  # newspage > span > span:nth-child(1) > a:nth-child(3)

        except:
            total_comment_page = 1

        if current_page < total_comment_page:
            target_page = current_page + 1
            target_url = sel.css(
                f'#newspage > span > span:nth-child(1) > a[data-page="{target_page}"]::attr(href)').get()
            # target_url = sel.css(f'#newspage > span > span:nth-child(1) > a:nth-child({child_number})::attr(href)').get()#newspage > span > span:nth-child(1) > a:nth-child(4)
            yield Request(url='https://guba.eastmoney.com{}'.format(target_url), callback=self.caifuhao_comment,
                          cb_kwargs={'stock': stock, 'current_page': target_page},
                          headers=self.header
                          )

        else:
            yield stock

    def closed(self, response):
        self.driver.quit()
        # pass


class Zazesus(total_page):
    name = '300612_1'

    def __init__(self, **kwargs):
        self.Stock_id = '688228'
        self.begin_page = 1
        self.end_page = 4
        self.tunnelhost = "k321.kdltps.com"
        self.tunnelport = "15818"
        self.proxy_username = "t17941167792939"
        self.proxy_password = "790msm5i"
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
        self.header = {"Connection": "close"}
        self.driver = webdriver.Chrome(chrome_options=chrome_options)


class Zazesus2(total_page):
    name = '300612_2'

    def __init__(self, **kwargs):

        self.Stock_id = '688228'
        self.begin_page = 5
        self.end_page = 8
        self.tunnelhost = "z766.kdltps.com"
        self.tunnelport = "15818"
        self.proxy_username = "t17948774858621"
        self.proxy_password = "7f49f6rj"
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
        self.header = {"Connection": "close"}
        self.driver = webdriver.Chrome(chrome_options=chrome_options)


class Zazesu3(total_page):
    name = '300612_3'

    def __init__(self, **kwargs):

        self.Stock_id = '688228'
        self.begin_page = 9
        self.end_page = 11
        self.tunnelhost = "u820.kdltps.com"
        self.tunnelport = "15818"
        self.proxy_username = "t17948798542595"
        self.proxy_password = "5aj2upmy"
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
        self.header = {"Connection": "close"}
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
