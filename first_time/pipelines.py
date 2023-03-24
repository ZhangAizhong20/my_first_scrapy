# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime
import json
from first_time.items import TotalPage
from itemadapter import ItemAdapter


class FirstTimePipeline:
    def process_item(self, item, spider):
        return item


import pymongo
from scrapy.exceptions import DropItem


def process_datetime(datetime_str):
    datetime_formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y年%m月%d日 %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
        '%Y/%m/%d %H:%M:%S',
        '%Y/%m/%d %H:%M',
        '%Y/%m/%d',
        '%Y年%m月%d日 %H:%M',
        '%Y年%m月%d日',
    ]
    try:
        for fmt in datetime_formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                pass
    except:
        return f'{datetime_str}_error'


def process_likes(like: str):
    if like == '点赞':
        return 0
    else:
        return int(like)


class MongoDBPipeline:

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        # self.mongo_collection = mongo_collection

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_URI'),
            mongo_db=crawler.settings.get('MONGODB_DATABASE', 'east'),
            # mongo_collection=crawler.settings.get('MONGODB_COLLECTION', 'mystocks')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        # self.collection = self.db[self.mongo_collection]
        # self.collection.create_index([('stock_id', pymongo.ASCENDING)], unique=False)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if not isinstance(item, TotalPage):
            raise DropItem('Item is not a Stock object')

        # 处理更新时间和发布时间
        data = dict(item)
        # data['update_time'] = datetime.strptime(data['update_time'], '%m-%d %H:%M')
        data['publish_time'] = process_datetime(data['publish_time'])
        # try:
        #     data['author_location'] = data['author_location'][-2:]
        # except:
        #     data['author_location'] = None
        # try:
        #     data['author_ip'] = data['author_ip'][3:]
        # except: data['author_ip'] = 'not exist'
        for comment in data['comments']:
            try:
                comment['author_location'] = comment['author_location'][-2:]
            except:
                comment['author_location'] = None
            comment['time'] = process_datetime(comment['time'])
            comment['likes'] = process_likes(comment['likes'])
        print(data)
        # comments = data.pop('comments')  # 取出评论列表
        # data['comments'] = json.dumps(comments)

        # data['comments'] = json.loads(comments)
        # comments_dicts = [dict(c) for c in comments]  # 将评论列表转换为字典列表
        # data['comments'] = comments_dicts  # 将转换后的评论字典列表加入到股票字典中
        collection_name = data['stock_id']
        if collection_name not in self.db.list_collection_names():
            self.db.create_collection(collection_name)

        collection = self.db[collection_name]
        collection.insert_one(data)
        # 将数据插入 MongoDB

        return item
