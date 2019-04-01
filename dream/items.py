# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DreamItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    item_name = scrapy.Field()
    item_category = scrapy.Field()
    item_link = scrapy.Field()
    item_price = scrapy.Field()
    item_seller = scrapy.Field()
    item_delivery = scrapy.Field()
    item_sales = scrapy.Field()
    item_description = scrapy.Field()
