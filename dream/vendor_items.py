# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class VendersDetails(scrapy.Item):
    seller_name = scrapy.Field()
    transactions = scrapy.Field()
    fe_enabled = scrapy.Field()
    join_date = scrapy.Field()
    last_active = scrapy.Field()
    status = scrapy.Field()
    total_rating = scrapy.Field()
    rating_table = scrapy.Field()
    more_ratings = scrapy.Field()
    profile = scrapy.Field()
    pgp = scrapy.Field()