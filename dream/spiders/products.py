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
from scrapy.utils.project import get_project_settings
settings = get_project_settings()
from dream.items import DreamItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
import traceback
from dream.spiders.util import register
# import requests
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
    name = 'market'
    custom_settings = {
        "FEED_URI": "items-"+ str(date.today()) + ".json"
    }
    
    def randomCookie(self):
        if not self.all_cookies:
            for i in self.total_cookies:
                self.all_cookies.append(i[1])
        return self.all_cookies.pop()

    def start_requests(self):
        self.total_cookies, self.main_url = register.initiate()
        try:
            open('./cookies.txt', 'w').close()
            with open('./cookies.txt', 'a') as cfile:
                for i in self.total_cookies:
                    print(i[1])
                    cfile.write(json.dumps(i[1]) +'\n')
        except:
            print('ERROR when saving ciijie file')
            print(traceback.format_exc())
        # a copy of total_cookies
        self.all_cookies = []
        self.item_count = 0
        print(color_s+'Hello, we are starting to call start_requests'+color_e)
        # yield Request(url=random.choice(self.main_url)+ start_page, headers=all_headers, cookies=self.randomCookie(), callback=self.parse, errback=self.errback_httpbin)
        yield Request(url=random.choice(self.main_url)+'/?page=1', headers=all_headers, cookies=self.randomCookie(), callback=self.iteratePages, errback=self.errback_httpbin)
    
    def iteratePages(self, response):
        num = int(response.xpath('//a[@class="pager "]/text()').extract()[-1])
        for i in range(1, num):
            yield Request(url=random.choice(self.main_url)+'/?page='+str(i), headers=all_headers, cookies=self.randomCookie(), callback=self.parse, errback=self.errback_httpbin)
    
    #Main parse, extract item list of a page
    def parse(self, response):
        # status = self.detect_errors(response)
        # if status[0] == 2:
        #     yield status[2]
        #     return
        entries = response.xpath('.//div[@class="around"]')
        if not entries:
            print('The number of items on page', response.request.url, 'is 0')
            yield Request(url=response.request.url, headers=all_headers, cookies=self.randomCookie(), callback=self.parse, errback=self.errback_httpbin, dont_filter=True)
            return
        for entry in entries:
            item = DreamItem()
            item['item_name'] = entry.xpath(
                './/div[@class="text oTitle"]/a/text()').extract()[0].strip()
            item['item_link'] = entry.xpath(
                './/div[@class="text oTitle"]/a/@href').extract()[0].strip()
            item['item_price'] = entry.xpath(
                './/div[@class="bottom oPrice"]/text()').extract()[0].strip()
            item['item_seller'] = entry.xpath(
                './/div[@class="oVendor"]/a[1]/text()').extract()[0].strip()
            item['item_delivery'] = entry.xpath(
                './/div[@class="oShips"]/span/text()').extract()[0].strip()
            # yield item
            currDomain = response.url.split('.onion/')[0] + '.onion'
            item_page_url = currDomain + item['item_link'].lstrip('.')
            yield Request(url=item_page_url, cookies=self.randomCookie(), meta={'item': item}, headers=all_headers, callback=self.parse_itempage, errback=self.errback_httpbin, dont_filter=True)

        # page_num = int(response.request.url.split('=')[1])
        # if page_num <= 4600:
        #     next_page_url = random.choice(self.main_url) + '/?page=' + str(page_num + 1)
        #     yield Request(url=next_page_url, cookies=self.randomCookie(), headers=all_headers, callback=self.parse, errback=self.errback_httpbin)

    # parse item page
    def parse_itempage(self, response):
        item = response.meta['item']
        # start 404 detect
        notfound = response.xpath('//img[@class="title"]/text()').extract()
        captcha = response.xpath('//div[@class="ddos"]/text()').extract()
        if notfound:
            item['item_sales'] = 'Page 404'
            yield item
            return
        elif captcha:
            print('got captcha')
        elif not response.xpath('.//div[@class="title"]'):
            yield Request(url=response.request.url, headers=all_headers, meta=response.meta, cookies=self.randomCookie(), callback=self.parse_itempage, errback=self.errback_httpbin, dont_filter=True)
            return
        # end 404 detect
        item_category = response.xpath('.//div[starts-with(@class,"category  selected")]/a/@href').extract()
        if item_category:
            item['item_category'] = item_category[0].split('=')[1]

        item['item_description'] = response.xpath('.//div[@id="offerDescription"]/pre/text()').extract()
        item['item_sales'] = response.xpath('.//td[@class="age dontwrap"]/text()').extract()
        if not item['item_sales']:
            item['item_sales'] = '0'
        yield item

        self.item_count += 1
        if self.item_count%1000 == 0:
            print('Scraped items:', self.item_count)

        
    def detect_errors(self, response):
        notfound = response.xpath('//img[@class="title"]/text()').extract()
        captcha = response.xpath('//div[@class="ddos"]/text()').extract()
        loggedout = response.xpath('//div[@class="login notloggedin register"]').extract()
        entries = response.xpath('.//div[@class="around"]')
        description = response.xpath('.//div[@id="offerDescription"]')
        new_url = random.choice(self.main_url)+'/'+response.request.url.split('/')[-1]
        status_code = 0 # 0 for continue, 1 for yield item, 2 for yield request
        # run into a 404 page
        item = response.request.meta['item']
        if notfound == "Listing not found" and bool(response.request.meta['item']):
            status_code = 1
            item['item_sales'] = 'Page 404'
            self.item_count += 1
            print('Scraped items:', self.item_count)
        # run into a captcha page
        elif bool(captcha) or bool(loggedout):
            status_code = 2
            cookie = response.request.cookies
            print(cookie)
            print('time to generate a new cookie!')
            # Deal with cookies
            if cookie in self.all_cookies:
                self.all_cookies.remove(cookie)
            for i in self.total_cookies:
                if i[1] == cookie:
                    username = i[0]
                    new = register.new_match(username=username)
                    self.total_cookies.remove(i)
                    self.total_cookies.append(new)
                    break
            if bool(response.request.meta['item']):
                req = Request(url=response.request.url, meta=response.meta, cookies=self.randomCookie(), headers=all_headers,  callback=self.parse_itempage, dont_filter=True, errback=self.errback_httpbin)
            else:
                req = Request(url=response.request.url, cookies=self.randomCookie(), headers=all_headers,  callback=self.parse, dont_filter=True, errback=self.errback_httpbin)
        # list page has no items
        elif bool(entries) is False and bool(response.request.meta['item']) is False:
            status_code = 2
            print('List page has no item', response.request.url, response.request.cookies)
            self.logger.error('List page has no item {}'.format(response.request.url))
            req = Request(url=new_url, cookies=self.randomCookie(), headers=all_headers,  callback=self.parse, dont_filter=True, errback=self.errback_httpbin)
        # list page has less than 32 items
        elif len(entries) < 32 and bool(response.request.meta['item']) is False:
            status_code = 2
            print('The number of items on page %s is smaller than 32' %response.request.url)
            self.logger.error('The number of items on page {} is smaller than 32'.format(response.request.url))
            req = Request(url=new_url, cookies=self.randomCookie(), headers=all_headers,  callback=self.parse, dont_filter=True, errback=self.errback_httpbin)
        # item page has no description
        elif bool(description) is False and bool(response.request.meta['item']):
            status_code = 2
            print('item page has no description', response.request.url)
            self.logger.error('item page has no description {}'.format(response.request.url))
            req = Request(url=new_url, meta=response.meta, cookies=self.randomCookie(), headers=all_headers,  callback=self.parse_itempage, dont_filter=True, errback=self.errback_httpbin)
        else:
            return False, False, False
        return status_code, item, req

    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type: _DataLoss
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
            yield Request(url=url, cookies=self.randomCookie(), meta=request.meta, headers=all_headers, callback=request.callback, errback=self.errback_httpbin, dont_filter=True)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
            print(request.__dict__.keys())
