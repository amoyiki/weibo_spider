# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from scrapy.conf import settings
from scrapy import log
from weibo.items import ProfileItem, FollowingItem, FollowedItem

class WeiboPipeline(object):
    def process_item(self, item, spider):
        return item

class MongoDBPipeline(object):
    def __init__(self):
        connection = MongoClient(
            host=settings['MONGODB_SERVER'],
            port=settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.info = db[settings['INFO']]
        self.following = db[settings['FOLLOWING']]
        self.followed = db[settings['FOLLOWED']]

    def process_item(self, item, spider):

        if isinstance(item, ProfileItem):
            self.info.insert(dict(item))
        elif isinstance(item, FollowingItem):
            self.following.insert(dict(item))
        elif isinstance(item, FollowedItem):
            self.followed.insert(dict(item))
        log.msg("Weibo  added to MongoDB database!",
                level=log.DEBUG, spider=spider)
        return item