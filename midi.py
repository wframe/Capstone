from __future__ import division
from scrapy.spiders import CrawlSpider, Rule
from scrapy.exceptions import CloseSpider
import matplotlib.pyplot as plt
from urlparse import urlparse
from scrapy.utils.httpobj import urlparse_cached
from os import path
import random as rand
import scrapy
import traceback
from scrapy.linkextractors import LinkExtractor
from inspect import currentframe, getframeinfo


class MidiSpider(CrawlSpider):
	name = "midispider"
	allowed_domains = ["midiworld.com/"]
	deny = ('',)
	start_urls = (
		'http://www.midiworld.com/files/',
	)
	def remove_querystring(url):
		o = urlparse(url)
		new_url = o.scheme + "://" + o.netloc + o.path
		return new_url
	rules = (
				Rule(LinkExtractor(allow=(r'.*',), deny=deny, process_value=remove_querystring), follow=True),
			)


	def process(self, response):
		reqs = []
		for link in LinkExtractor().extract_links(response):
			req = self.make_requests_from_url(link.url)				
			reqs.append(req)
		return reqs