# -*- coding: utf-8 -*-
import scrapy


class PageItem(scrapy.Item):
    """
    The scrapy page item class holding the page content after crawling it..
    """
    title = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    referer = scrapy.Field()

    def __repr__(self):
        return repr({'Page Url': self['url']})
