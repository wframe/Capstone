# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from midispider.items import MidispiderItem
import uuid



class MidiworldSpider(CrawlSpider):
    name = 'midiworld'
    allowed_domains = ['midiworld.com']
    start_urls = ['http://www.midiworld.com/files']

    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )
    def parse_item(self, response):
        if 'download' in response.url: 
            if 'application/octet-stream' in response.headers['Content-Type']:
                with open(response.url.split('/download/')[1]+'.mid','wb') as f:
                    f.write(response.body)
