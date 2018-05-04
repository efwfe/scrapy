# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy import Request

from zhihuuser.items import UserItem


class ZhihuSpider(scrapy.Spider):
    name = "zhihu2"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['http://www.zhihu.com/']

    start_user = "xiang-huan-zhong"
    user_url = "https://www.zhihu.com/api/v4/members/{user}?include={include}"
    user_query = "allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics"

    follower_url = "https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}"
    follower_query = "data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics"

    def start_requests(self):
        yield Request(self.user_url.format(user=self.start_user, include=self.user_query), self.parse_user)
        yield Request(self.follower_url.format(user=self.start_user, include=self.follower_query, offset=0, limit=20),
                      callback=self.parse_follower)

    # 获取用户资料
    def parse_user(self, response):
        result = json.loads(response.text)
        item = UserItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item

        # 获取关注列表
        yield Request(
            self.follower_url.format(user=result.get('url_token'), include=self.follower_query, offset=0, limit=20),
            callback=self.parse_follower)

    # 获取关注用户，调价跳转
    def parse_follower(self, resonse):
        results = json.loads(resonse.text)
        if 'data' in results.keys():
            for result in results.get("data"):
                yield Request(self.user_url.format(user=result.get("url_token"), include=self.user_query),
                              callback=self.parse_user)

        if 'paging' in results.keys() and results.get("paging").get("is_end") == False:
            next_page = results.get("paging").get("next")
            yield Request(next_page, callback=self.parse_follower)
