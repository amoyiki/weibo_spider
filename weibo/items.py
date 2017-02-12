# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class WeiboItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ProfileItem(Item):
    """
    账号的微博数、关注数、粉丝数及详情
    """
    _id = Field()
    nick_name = Field()
    profile_pic = Field()
    tweet_stats = Field()
    following_stats = Field()
    follower_stats = Field()
    sex = Field()
    location = Field()
    birthday = Field()
    bio = Field()

class FollowingItem(Item):
    """
    关注的微博账号
    """
    _id = Field()
    relationship = Field()

class FollowedItem(Item):
    """
    粉丝的微博账号
    """
    _id = Field()
    relationship = Field()