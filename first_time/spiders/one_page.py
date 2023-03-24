import scrapy
from scrapy import Request, Selector
# from first_time.items import MovieItem
from bs4 import BeautifulSoup
import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.http import HtmlResponse
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from first_time.items import Comment, OnePage, Subcomment, TotalPage

class OnePageSpider(scrapy.Spider):
    name = 'mainpage'
    allowed_domains = ['guba.eastmoney.com']
    # start_urls = ['https://guba.eastmoney.com/news,600895,1287541588.html']

    def __init__(self):
            #实例化一个浏览器对象(实例化一次)
            self.driver = webdriver.Chrome()


    def start_requests(self):
        # yield Request(url = 'https://guba.eastmoney.com/news,601985,1285818420.html')
        yield Request(url= 'https://caifuhao.eastmoney.com/news/20230315231912163418480?from=guba&name=5byg5rGf6auY56eR5ZCn&gubaurl=aHR0cDovL2d1YmEuZWFzdG1vbmV5LmNvbS9saXN0LDYwMDg5NS5odG1s')
        # yield SeleniumRequest(
        #             url=url, 
        #             callback=self.parse, 
        #             wait_time=10,
        #             wait_until=EC.element_to_be_clickable((By.CLASS_NAME, 'quote'))
        #             )


    #line2 > div.post_author_info.fl.cl > span.post_ip.fl
    # def parse(self, response:HtmlResponse):

    #     # html = self.driver.page_source.encode('utf-8')
    #     # response = HtmlResponse(url=response.url, body=html, encoding='utf-8')
    #     # sel = Selector(response)
    #     current_page = TotalPage()
    #     # html = response.text  # 将网页源码转换格式为html
    #     # soup = BeautifulSoup(html, features="lxml")
    #     # # print(html)
    #     # current_page['maintext'] = soup.find('div', 'article-body').get_text()
    #     # current_page['author'] = sel.css('#line2 > div.post_author_info.fl.cl > span.author_name.fl > strong > a > font::text').extract_first()  #line2 > div.post_author_info.fl.cl > span.author_name.fl > strong > a > font
    #     # current_page['author_ip'] = sel.css('#line2 > div.post_author_info.fl.cl > span.post_ip.fl::text').extract_first()
    #     # current_page['publish_time'] = sel.css('#line2 > div.post_author_info.fl.cl > span.post_time.fl::text').extract_first()


    #     # comment_url = 

    #     sel = Selector(response)
    #     html = response.text  # 将网页源码转换格式为html
    #     soup = BeautifulSoup(html, features="lxml")
    #     # stock = kwargs['stock']
    #     # print(html)
    #     current_page['maintext'] = soup.find('div', 'article-body').get_text()
    #     current_page['author'] = sel.css('#main > div.grid_wrapper > div.grid > div.g_content > div.article.page-article > div.article-head > div.article-meta > span.item > a::text').extract_first()  #authorwrap > a
    #     current_page['author_ip'] = sel.css('#main > div.grid_wrapper > div.grid > div.g_content > div.article.page-article > div.article-head > div.article-meta > span:nth-child(3)::text').extract_first()
    #     current_page['publish_time'] = sel.css('#main > div.grid_wrapper > div.grid > div.g_content > div.article.page-article > div.article-head > div.article-meta > span:nth-child(2)::text').extract_first()

    #     print(current_page)

    


        # comment_list = sel.css('#comment_all_content > div > div')

        # # current_page['comment'] = sel.css('#comment_all_content > div > div:nth-child(3) > div > div.level1_reply_cont > div.full_text::text').get()#comment_all_content > div > div:nth-child(3) > div > div.level1_reply_cont > div.full_text

        # for comment in comment_list:
        #     #comment_all_content > div > div:nth-child(1) > div > div.replyer_info > a
        #     #comment_all_content > div > div:nth-child(2) > div > div.replyer_info.clearfix > div.userbox.fl > a
        #     com = Comment()#comment_all_content > div > div:nth-child(1) > div > div.replyer_info.clearfix > div.userbox.fl > a
        #     com['author'] = comment.css('div > div.replyer_info > a::text,div > div.replyer_info.clearfix > div.userbox.fl > a::text').get()#comment_all_content > div > div:nth-child(1) > div > div.replyer_info.clearfix > div.userbox.fl > a
        #     com['time'] = comment.css('div > div.publish_time > span:nth-child(1)::text').get() #comment_all_content > div > div:nth-child(1) > div > div.publish_time > span:nth-child(1)
        #     try:
        #         com['likes'] = comment.css('div > div.news_reply_btns.clearfix > div > span.level1_rebtn.replylike.unlike > span::text').get()
        #     except: pass

        #     com['author_location'] = comment.css('div > div.publish_time > span:nth-child(2)::text').get()#comment_all_content > div > div:nth-child(4) > div > div.publish_time > span:nth-child(2)
        #     com['text'] = comment.css('div > div.level1_reply_cont > div.short_text::text').get()
        #     print(com)
#comment_all_content > div > div:nth-child(4) > div > div.level2_box > div.level2_list > div:nth-child(1) > div.row1 > span.l2_short_text
#comment_all_content > div > div:nth-child(4) > div > div.level2_box > div.level2_list > div:nth-child(2)
#comment_all_content > div > div:nth-child(4) > div > div.level2_box > div.level2_list > div:nth-child(2) > div.row1 > span.l2_short_text
#comment_all_content > div > div:nth-child(2) > div > div.level2_box > div.level2_list > div.level2_item > div.row1 > span.l2_short_text
#comment_all_content > div > div:nth-child(4) > div > div.level2_box > div.level2_list > div:nth-child(2)
#comment_all_content > div > div:nth-child(4) > div > div.level2_box > div.level2_list > div:nth-child(2) > div.row1 > span.l2_short_text
#comment_hot_content > div > div:nth-child(1) > div > div.level1_reply_cont > div.short_text
#comment_all_content > div > div:nth-child(1) > div > div.level1_reply_cont > div.short_text
#comment_all_content > div > div:nth-child(21) > div > div.level2_box > div.level2_list > div.level2_item.previewL2 > div.row1 > span.l2_short_text
        #     subcomments = comment.css('div > div.level2_box > div.level2_list > div, div.level2_item , div.level2_item.previewL2')#comment_all_content > div > div:nth-child(1) > div > div.level2_box > div.level2_list
        #     for subcomment in subcomments:
        #         subcom = Subcomment()
        #         try:
                    
        #             subcom['subauthor'] = subcomment.css('div.row1 > span.replyer > a::text').get()
        #             subcom['subtext'] = subcomment.css('div.row1 > span.span.l2_short_text::text').get()#comment_all_content > div > div:nth-child(13) > div > div.level2_box > div.level2_list > div.level2_item.previewL2 > div.row1 > span.l2_short_text
        #             subcom['subtime'] = subcomment.css('div.row2.clearfix > span.time.fl::text').get()#comment_all_content > div > div:nth-child(4) > div > div.level2_box > div.level2_list > div:nth-child(2) > div.row1 > span.l2_short_text
        #             subcom['subauthor_location'] = subcomment.css('div.row2.clearfix > span.reply_ip::text').get()
                

        #             try:
        #                 subcom['sublikes'] = subcomment.css('div.row2.clearfix > div > span.level2_rebtn.replylike.haslike > span::text').get()
        #             except:break

        #         except:break


        #         print(subcom)
        #         com.add_subcomment(subcom)

        #     current_page.add_comment(com)
        # yield current_page

    def norm_full_page(self,response:HtmlResponse,**kwargs):

            
            sel = Selector(response)
            html = response.text  # 将网页源码转换格式为html
            soup = BeautifulSoup(html, features="lxml")
            stock = kwargs['stock']
            # print(html)
            stock['maintext'] = self.clear_str(soup.find('div', {'id': 'post_content'}).text)
            stock['author'] = sel.css('#line2 > div.post_author_info.fl.cl > span.author_name.fl > strong > a > font::text').extract_first()  #line2 > div.post_author_info.fl.cl > span.author_name.fl > strong > a > font
            stock['author_ip'] = sel.css('#line2 > div.post_author_info.fl.cl > span.post_ip.fl::text').extract_first()
            stock['publish_time'] = sel.css('#line2 > div.post_author_info.fl.cl > span.post_time.fl::text').extract_first()
            com_page = 1
            try:
                com_page = int(sel.css('#newspage > span > span:nth-child(1) > span::text').get())#newspage > span > span:nth-child(1) > span
            except:pass


            if 1 < com_page:
                #newspage > span > span:nth-child(1) > a.on
                #newspage > span > span:nth-child(1) > a:nth-child(3)
                target_page = 1
                
                target_url = sel.css(f'#newspage > span > span:nth-child(1) > a:nth-child({target_page+1})::attr(href)').get()#newspage > span > span:nth-child(1) > a:nth-child(4)
                #newspage > span > span:nth-child(1) > a:nth-child(3)
                yield Request(url= 'https://guba.eastmoney.com{}'.format(target_url),callback=self.norm_comment,cb_kwargs={'stock':stock,'current_page':target_page,'total_page':com_page})

            else:
                comment_list = sel.css('#comment_all_content > div > div')#comment_all_content > div > div:nth-child(1) > div

                for comment in comment_list:
                    com = Comment()
                    com['author'] = comment.css('div.replyer_info > a::text').get()
                    com['time'] = comment.css('div > div.publish_time > span:nth-child(1)::text').get() #comment_all_content > div > div:nth-child(1) > div > div.publish_time > span:nth-child(1)
                    try:
                        com['likes'] = comment.css('div > div.news_reply_btns.clearfix > div > span.level1_rebtn.replylike.unlike > span::text').get()
                    except: pass

                    com['author_location'] = comment.css('div > div.publish_time > span:nth-child(2)::text').get()#comment_all_content > div > div:nth-child(4) > div > div.publish_time > span:nth-child(2)
                    com['text'] = comment.css('div > div.level1_reply_cont > div.short_text::text').get()#comment_all_content > div > div:nth-child(1) > div > div.level1_reply_cont > div.short_text
                    stock['comments'].append(dict(com))
                    # stock.add_comment(com)
    def closed(self, reason):
        self.driver.quit()
                #comment_all_content > div > div:nth-child(4) > div > div.level2_box > div.level2_list > div:nth-child(1)
            #comment_all_content > div > div:nth-child(3) > div > div.publish_time > span:nth-child(1)
            #comment_all_content > div > div:nth-child(3) > div > div.level1_reply_cont > div.short_text
            #comment_all_content > div > div:nth-child(1) > div > div.replyer_info > a
        #comment_all_content > div > div:nth-child(1) > div > div.replyer_info > a
        #comment_all_content > div
        #comment_all_content > div > div:nth-child(1)
        #line2 > div.post_author_info.fl.cl > span.author_name.fl > strong > a > font
        
# def get_full_text(self, data_json):
#         """
#         the href of each item have different fartherPath:
#             1、https://caifuhao
#             2、http://guba.eastmoney.com

#         :param data_json: the json data lack full text
#         :return: the data json with full text
#         """
#         if 'caifuhao' in data_json['href']:
#             url = 'https:' + data_json['href']
#             soup = self.get_soup_form_url(url)
#             try:
#                 data_json['full_text'] = soup.find('div', 'article-body').get_text()
#                 return data_json

#             except ValueError as e:
#                 logging.debug('{} get null content'.format(data_json['href']))
#                 return data_json

#         elif '/new' in data_json['href']:
#             url = 'http://guba.eastmoney.com' + data_json['href']
#             soup = self.get_soup_form_url(url)
#             try:
#                 data_json['full_text'] = self.clear_str(soup.find('div', {'id': 'post_content'}).text)
#                 return data_json
#             except ValueError as e:
#                 logging.debug('{} get null content'.format(data_json['href']))
#         else:
#             logging.info('{} is not in exit ip'.format(data_json['href']))
#             return data_json