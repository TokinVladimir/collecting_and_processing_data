# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from multiprocessing import connection
from itemadapter import ItemAdapter
from pymongo import MongoClient
import pymongo

class NewparserPipeline:
    def __init__(self):
        client = MongoClient('192.168.8.3', 27017)
        self.mongobase = client.books

        # client = MongoClient('192.168.8.3', 27017)
        # mydb = client['books']
        # self.post = mydb['books']

    def process_item(self, item, spider):
        collection = self.mongobase[spider.name]
        collection.insert_one(item) 

        return item

