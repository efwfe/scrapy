# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy import Request

from zhihuuser.items import UserItem


class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['http://www.zhihu.com/']

    start_user = "xiang-huan-zhong"
    user_url = "https://www.zhihu.com/api/v4/members/{user}?include={include}"
    user_query = "allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics"
    follower_url = "https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}"
    follower_query = "data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics"

    def start_requests(self):
        yield Request(self.user_url.format(user=self.start_user, include=self.user_query), self.parse)
        # yield Request(self.follower_url.format(user=self.start_user, include=self.follower_query, offset=0, limit=20),
        #               callback=self.parse)

    def parse(self, response):
        result = json.loads(response.text)
        item = UserItem()
        for field in item.fields:
            if field in result:
                item[field] = result.get(field)
        yield item
