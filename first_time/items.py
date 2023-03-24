import scrapy


class MovieItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    rank = scrapy.Field()
    subject = scrapy.Field()


class StockItem(scrapy.Item):
    view_number = scrapy.Field()
    title = scrapy.Field()
    comment_number = scrapy.Field()
    author = scrapy.Field()
    update = scrapy.Field()
    it_url = scrapy.Field()

class OnePage(scrapy.Item):
    main_text = scrapy.Field()
    author = scrapy.Field()
    location = scrapy.Field()
    comment = []
    time = scrapy.Field()

class Comment(scrapy.Item):
    text = scrapy.Field()
    author = scrapy.Field()
    likes = scrapy.Field()
    author_location = scrapy.Field()
    time = scrapy.Field()
    subcomments = scrapy.Field(serializer=lambda x: [dict(item) for item in x])
    def add_subcomment(self, subcomment):
        self.setdefault('subcomments', []).append(subcomment)


class Subcomment(scrapy.Item):
    subtext = scrapy.Field()
    subauthor = scrapy.Field()
    sublikes = scrapy.Field()
    subauthor_location = scrapy.Field()
    subtime = scrapy.Field()


class TotalPage(scrapy.Item):
    stock_id = scrapy.Field(serializer=str)
    current_page = scrapy.Field(serializer=int)
    total_page_number = scrapy.Field(serializer=int)
    view_number = scrapy.Field()
    title = scrapy.Field()
    comment_number = scrapy.Field()
    author = scrapy.Field()
    update_time = scrapy.Field()
    it_url = scrapy.Field()
    publish_time = scrapy.Field()
    maintext = scrapy.Field()
    comments = scrapy.Field(serializer=lambda x: [dict(item) for item in x])
    # comments = scrapy.Field()
    main_text = scrapy.Field()
    author_ip = scrapy.Field()

    # def add_comment(self, comment):
    #     self.setdefault('comments', []).append(comment)
        