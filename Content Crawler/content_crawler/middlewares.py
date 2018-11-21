# -*- coding: utf-8 -*-
from scrapy import signals
from scrapy.http import Request
# from items import PageItem
import re
from six.moves.urllib.parse import urlparse
import logging
from scrapy.exceptions import IgnoreRequest

logger = logging.getLogger(__name__)


class DuplicateFilterMiddleware(object):
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to connect the middle to the spider
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        """
        Main function for the duplicate filter middle ware
        Uses the duplicate filter model to either download or ignore the request..
        :param request: the request to be processed
        :param spider: the spider using the middle ware
        :return:
        """
        # Called for each request that goes through the downloader
        # middleware.
        if request.meta["parent_page"] == "":
            return
        if spider.dup_filter.model_predict(request.meta["parent_page"], request.url):
            open("duplicated_bo.txt", "a").write(request.meta["parent_page"] + "\n" + request.url + "\n\n\n")
            raise IgnoreRequest()

        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        logger.info('Spider opened: %s' % spider.name)

