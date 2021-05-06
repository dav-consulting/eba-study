# -*- coding: utf-8 -*-
import scrapy


class FetchEvaluationsItem(scrapy.Item):
    """Scrapy items for scraped meta data and the files/evaluations"""

    title = scrapy.Field()
    publication_date = scrapy.Field()
    series = scrapy.Field()
    series_number = scrapy.Field()
    language = scrapy.Field()
    issued = scrapy.Field()
    authors = scrapy.Field()
    description = scrapy.Field()
    doc_url = scrapy.Field()
    # doc_id = scrapy.Field()
    # eba_2017_12 = scrapy.Field()
    # eba_2017_12_score = scrapy.Field()

    file_urls = scrapy.Field()  ## test downloader
    files = scrapy.Field()
