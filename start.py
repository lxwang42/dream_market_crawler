# -*- coding: utf-8 -*-

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

processM = CrawlerProcess(get_project_settings())
processM.crawl('market')
processM.start(stop_after_crawl=False) # the script will block here until the crawling is finished

processS = CrawlerProcess(get_project_settings())
processS.crawl('sellers')
processS.start()


# import json
# with open('./items.json') as ilist:
#     items = [json.loads(jline.strip()) for jline in ilist]
#     print(items[0]['item_seller'])
# for v in items:
#     vender_page =  "/contactMember?member=" + v['item_seller'] + "&tab=ratings"
#     print(vender_page)
