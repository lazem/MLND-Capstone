import scrapy
from scrapy.http import Request, HtmlResponse
from .. import items
from scrapy.linkextractors import LinkExtractor
from six.moves.urllib.parse import urlparse
import re
from scrapy.exceptions import CloseSpider
from scrapy.utils.project import get_project_settings
from .. import dup_detect_filter




class ContentSpider(scrapy.Spider):
    name = "content"

    def __init__(self, url=""):
        """
        Initialize the content spider
        :param url: the starting url to begin crawling
        """

        # self.url = 'https://ubuntuforums.org'
        if url:
            self.url = url

        # define a link extractor for the spider..
        self.link_extractor = LinkExtractor()
        self.link_extractor.canonicalize = False

        # to ignore any outer domain from getting crawled
        self.allowed_domains = [re.sub(r'^www\.', '', urlparse(self.url).hostname)]

        # number of pages to crawl
        self.COUNT_MAX = 100
        self.count = 0

        # create instance of the duplicate filter deployed model..
        # uncomment this if the model is used..
        settings = get_project_settings()
        middlewares = settings.get('DOWNLOADER_MIDDLEWARES')
        if middlewares and 'DuplicateFilterMiddleware' in middlewares.keys():
            self.dup_filter = dup_detect_filter.DuplicateFilter()

    def start_requests(self):
        """
        Create the starting request for the spider.
        :return: scrapy request object(s)
        """
        urls = [
            self.url,
        ]
        # the meta dict is used here in case the duplicate filter is activated,
        # to pass the parent url
        # the parent_page is empty to ignore the first url..
        meta = dict({'parent_page':""})
        for url in urls:
            yield scrapy.Request(url=url, meta=meta, callback=self.parse)

    def parse(self, response):
        """
        The spider call back function after a page is downloaded
        :param response: scrapy response object containing page content
        :return: scrapy item (the page content to be processed) plus additional requests
        """

        page = self._get_item(response)
        r = [page]
        self.count += 1
        # close the spider if a definite number of pages is crawled..
        if (self.count > self.COUNT_MAX):
            raise CloseSpider(reason='The watcher is no longer active.')
        # extract further requests from the page..
        rs = self._extract_requests(response)
        if rs:
            r.extend(rs)
        return r

    def _get_item(self, response):
        """
        create instance of page item class from the response object
        :param response: scrapy page response
        :return: scrapy page item
        """
        item = items.PageItem(
            url=response.url,
            content=response.body,
            referer=response.request.headers.get('Referer'),
        )

        self._set_title(item, response)
        return item

    def _set_title(self, page, response):
        # extract the page title from the page html
        if isinstance(response, HtmlResponse):
            title = response.xpath("//title/text()").extract()
            if title:
                page['title'] = title[0]

    def _extract_requests(self, response):
        """
        extract further requests from the page response object 
        :param response: the page response object to be processed
        :return: list of scrapy requests
        """
        all_links = self.link_extractor.extract_links(response)

        meta = dict({'parent_page': response.url})
        r = []
        r.extend(Request(x.url, meta=meta, callback=self.parse) for x in all_links)
        return r
