# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urljoin
from scrapy import Request
from jianshu.items import JianshuItem
import re
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
from scrapy_splash import SplashMiddleware
from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector

class JianshuSpiderSpider(scrapy.Spider):
    name = 'jianshu_spider'
    allowed_domains = ['jianshu.com']
    start_urls = ['https://www.jianshu.com/c/V2CqjW']
    header = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
    }
    page_number = 1

    def parse(self, response):
        urls = response.xpath('//*[@class="title"]/@href')
        for url in urls:
            abs_url = response.urljoin(url.extract())
            yield SplashRequest(abs_url, self.parse_content, args={'wait': '0.5'})

        self.page_number = self.page_number + 1
        next_url = 'https://www.jianshu.com/c/V2CqjW?order_by=added_at&page=' + str(self.page_number)
        yield Request(next_url, headers=self.header, callback=self.parse)

    def parse_content(self, response):
        Item = JianshuItem()
        site = Selector(response)
        Item['title'] = site.xpath('//*[@class="article"]/h1/text()').extract()
        Item['author'] = site.xpath('//*[@class="author"]/div/span/a/text()').extract()
        Item['publishtime'] = site.xpath('//*[@class="publish-time"]/text()').extract()
        Item['word_count'] = site.xpath('//*[@class="wordage"]/text()').re('(\d+)')
        Item['view_count'] = site.xpath('//*[@class="views-count"]/text()').re('(\d+)')
        Item['comment_count'] = site.xpath('//*[@class="comments-count"]/text()').re('(\d+)')
        Item['like_count'] = site.xpath('//*[@class="likes-count"]/text()').re('(\d+)')
        content_pre = site.xpath('//*[@class="show-content-free"]')[0].extract()
        Item['content'] = re.sub('<.*?>', '', content_pre).replace("\n", ' ')

        yield Item




