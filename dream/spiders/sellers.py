# -*- coding: utf-8 -*-
# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import random
import string
import json
from scrapy import Request, FormRequest
from scrapy.spiders import Spider
from dream.vendor_items import VendersDetails
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
# import traceback
from dream.spiders.util import register
from datetime import date
from twisted.web.client import ResponseFailed

color_s = "\033[92m"
color_e = "\033[0m"
all_headers = {'Host': 'pjaopjqvjk6be4wz.onion',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Language': 'en-US,en;q=0.5',
               'Accept-Encoding': 'gzip, deflate',
               'Connection': 'keep-alive'}
# self.main_url = ['http://pjaopjqvjk6be4wz.onion','http://jd6yhuwcivehvdt4.onion','http://t3e6ly3uoif4zcw2.onion',
#             'http://7ep7acrkunzdcw3l.onion','http://vilpaqbrnvizecjo.onion','http://igyifrhnvxq33sy5.onion',
#             'http://6qlocfg6zq2kyacl.onion','http://x3x2dwb7jasax6tq.onion','http://bkjcpa2klkkmowwq.onion',
#             'http://xytjqcfendzeby22.onion','http://nhib6cwhfsoyiugv.onion','http://k3pd243s57fttnpa.onion',
#             ]


class MarketSpider(Spider):
    name = 'sellers'
    custom_settings = {
        "FEED_URI": "sellers-"+ str(date.today()) + ".json"
    }

    def randomCookie(self):
        if not self.all_cookies:
            for i in self.total_cookies:
                # self.all_cookies.append(i[1])
                self.all_cookies.append(i)
        return self.all_cookies.pop()

    def start_requests(self):
        self.main_url = ['http://pjaopjqvjk6be4wz.onion']
        self.total_cookies = []
        try:
            with open('./cookies.txt') as cfile:
                for i in cfile:
                    self.total_cookies.append(json.loads(i.strip()))
        except:
            print('reading cookie file failed')
        # a copy of total_cookies
        print(self.total_cookies)
        self.all_cookies = []
        print(color_s+'Hello, we are starting to call start_requests for sellers'+color_e)
        # yield Request(url=random.choice(self.main_url)+ start_page, headers=all_headers, cookies=self.randomCookie(), callback=self.parse, errback=self.errback_httpbin)
        # http://nhib6cwhfsoyiugv.onion/contactMember?member=C_u_CAB_Schweiz&tab=ratings
        with open("./items-" + str(date.today()) + ".json") as ilist:
            items = [json.loads(jline.strip()) for jline in ilist]
        for v in items:
            vender_page = random.choice(self.main_url) + "/contactMember?member=" + v['item_seller'] + "&tab=ratings"
            print(vender_page)
            yield Request(url=vender_page, headers=all_headers, cookies=self.randomCookie(), callback=self.parse, errback=self.errback_httpbin)
    
    def parse(self, response):
        item = VendersDetails()
        if not response.xpath('.//div[@class="title"]/text()'):
            print('Cant find contact info on page{} cookie {}'.format(response.url, response.request.cookies))
            yield Request(url=response.url, headers=all_headers, cookies=self.randomCookie(), callback=self.parse, errback=self.errback_httpbin, dont_filter=True)
            return
        transactions = response.xpath('.//span[@title="Successful transactions"]/text()')[0].extract().strip('(').strip(')')
        fe_enabled = response.xpath('.//div[label[text()="FE enabled"]]/span/text()')[0].extract().strip()
        join_data = response.xpath('.//div[@class="memberSince"]/span/text()')[0].extract().strip()
        last_active = response.xpath('.//div[label[text()="Last active"]]/span/text()')[0].extract().strip()
        item['status'] = 'N/A'
        if response.xpath('.//div[label[text()="Status"]]/span/text()'):
            status = response.xpath('.//div[label[text()="Status"]]/span/text()')[0].extract().strip()
            item['status'] = status
        total_rating = response.xpath('.//table[@class="centerDefault hoverable"]/tbody/tr')
        rating_table = response.xpath('.//table[@class="ratingTable hoverable"]/tbody/tr')
        more_ratings = '0'
        if response.xpath('.//div[@class="andMoreRatings"]/text()'):
            more_ratings = response.xpath('.//div[@class="andMoreRatings"]/text()')[0].extract().strip().split(' ')[1]

        item['seller_name'] = response.url.split('=')[1].split('&')[0]
        item['transactions'] = transactions
        item['fe_enabled'] = fe_enabled
        item['last_active'] = last_active
        item['join_date'] = join_data
        item['total_rating'] = []
        item['rating_table'] = []
        item['more_ratings'] = more_ratings
        for i in total_rating:
            row = []
            col = i.xpath('./td')
            for c in col:
                text = c.xpath('./text()')[0].extract().strip()
                row.append(text)
            item['total_rating'].append(row)
        for i in rating_table:
            # item['rating_table'].append([])
            row = []
            col = i.xpath('./td')
            for c in col:
                text = c.xpath('./text()')[0].extract().strip()
                if text != '':
                    row.append(text)
            item['rating_table'].append(row)
        urlProfilePage = response.request.url.split('&tab=')[0]
        yield Request(url=urlProfilePage, meta={'item':item}, headers=all_headers, cookies=self.randomCookie(), callback=self.profilePage, errback=self.errback_httpbin)


    def profilePage(self, response):
        item = response.meta['item']
        if not response.xpath('.//div[@class="title"]/text()'):
            print('Cant find contact info on page{} cookie {}'.format(response.url, response.request.cookies))
            yield Request(url=response.url, headers=all_headers, meta=response.meta, cookies=self.randomCookie(), callback=self.parse, errback=self.errback_httpbin, dont_filter=True)
            return
        item['profile'] = 'N/A'
        item['pgp'] = 'N/A'
        if response.xpath('.//pre[not (@class)]'):
            item['profile'] = response.xpath('.//pre[not (@class)]/text()')[0].extract().strip()
        if response.xpath('.//pre[@class="code"]'):
            item['pgp'] = response.xpath('.//pre[@class="code"]/text()')[0].extract().strip()
        yield item

    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:
        if failure.check(ResponseFailed):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            request = failure.request
            self.logger.error('Retrying Data loss on %s', response.url)
            url = random.choice(self.main_url) + '/' + request.url.split('.onion/')[1]
            yield Request(url=url, cookies=self.randomCookie(), meta=request.meta, headers=all_headers, callback=request.callback, errback=self.errback_httpbin, dont_filter=True)


        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            request = failure.request
            self.logger.error('Retrying HttpError on %s', response.url)
            url = random.choice(self.main_url) + '/' + request.url.split('.onion/')[1]
            yield Request(url=url, cookies=self.randomCookie(), meta=request.meta, headers=all_headers, callback=request.callback, errback=self.errback_httpbin)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
            print(request.__dict__.keys())