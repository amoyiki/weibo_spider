# -*- coding: utf-8 -*-
import scrapy
from scrapy.exceptions import CloseSpider
from weibo.items import ProfileItem, FollowingItem, FollowedItem
import re
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

class WeiboSpiderSpider(scrapy.Spider):
    name = "weibo_spider"
    allowed_domains = ["weibo.cn"]
    url = "http://weibo.cn/"
    start_urls = ['1799468404','5658208771','3804964543','5285316854','5268395811','6122777230','5503864294',
                  '2973825563','6042041854','5399305296','6112967033','5958250307','5899993712'] # 爬取入口微博ID
    task_set = set(start_urls) # 待爬取集合
    tasked_set = set() # 已爬取集合
    scrapy.core
    def start_requests(self):
        while len(self.task_set) > 0 :
            _id = self.task_set.pop()
            if _id in self.tasked_set:
                raise CloseSpider(reason="已存在该数据 %s "% (_id) )
            self.tasked_set.add(_id)
            info_url = self.url + _id
            info_item = ProfileItem()
            following_url = info_url + "/follow"
            following_item = FollowingItem()
            following_item["_id"] = _id
            following_item["relationship"] = []
            follower_url = info_url + "/fans"
            follower_item = FollowedItem()
            follower_item["_id"] = _id
            follower_item["relationship"] = []
            yield scrapy.Request(info_url, meta={"item":info_item}, callback=self.account_parse)
            yield scrapy.Request(following_url, meta={"item":following_item}, callback=self.relationship_parse)
            yield scrapy.Request(follower_url, meta={"item":follower_item}, callback=self.relationship_parse)

    def account_parse(self, response):
        item = response.meta["item"]
        sel = scrapy.Selector(response)
        profile_url = sel.xpath("//div[@class='ut']/a/@href").extract()[1]
        counts = sel.xpath("//div[@class='u']/div[@class='tip2']").extract_first()
        item['_id'] = re.findall(u'^/(\d+)/info',profile_url)[0]
        item['tweet_stats'] = re.findall(u'微博\[(\d+)\]', counts)[0]
        item['following_stats'] = re.findall(u'关注\[(\d+)\]', counts)[0]
        item['follower_stats'] = re.findall(u'粉丝\[(\d+)\]', counts)[0]
        if int(item['tweet_stats']) < 4500 and int(item['following_stats']) > 1000 and int(item['follower_stats']) < 500:
            raise CloseSpider("僵尸粉")
        yield scrapy.Request("http://weibo.cn"+profile_url, meta={"item": item},callback=self.profile_parse)

    def profile_parse(self,response):
        item = response.meta['item']
        sel = scrapy.Selector(response)
        info = sel.xpath("//div[@class='tip']/following-sibling::div[@class='c']").extract_first()
        item["profile_pic"] = sel.xpath("//div[@class='c']/img/@src").extract_first()
        item["nick_name"] = re.findall(u'昵称:(.*?)<br>',info)[0]
        item["sex"] = re.findall(u'性别:(.*?)<br>',info) and re.findall(u'性别:(.*?)<br>',info)[0] or ''
        item["location"] = re.findall(u'地区:(.*?)<br>',info) and re.findall(u'地区:(.*?)<br>',info)[0] or ''
        item["birthday"] = re.findall(u'生日:(.*?)<br>',info) and re.findall(u'生日:(.*?)<br>',info)[0] or ''
        item["bio"] = re.findall(u'简介:(.*?)<br>',info) and re.findall(u'简介:(.*?)<br>',info)[0] or ''
        yield item

    def relationship_parse(self, response):
        item = response.meta["item"]
        sel = scrapy.Selector(response)
        uids = sel.xpath("//table/tr/td[last()]/a[last()]/@href").extract()
        new_uids = []
        for uid in uids:
            if "uid" in uid:
                new_uids.append(re.findall('uid=(\d+)&',uid)[0])
            else:
                try:
                    new_uids.append(re.findall('/(\d+)', uid)[0])
                except:
                    print('--------',uid)
                    pass
        item["relationship"].extend(new_uids)
        for i in new_uids:
            if i not in self.tasked_set:
                self.task_set.add(i)
        next_page = sel.xpath("//*[@id='pagelist']/form/div/a[text()='下页']/@href").extract_first()
        if next_page:
            yield scrapy.Request("http://weibo.cn"+next_page, meta={"item": item},callback=self.relationship_parse)
        else:
            yield item
