# -*- coding: utf-8 -*-

# Scrapy settings for content_crawler project
#

BOT_NAME = 'content_crawler'

SPIDER_MODULES = ['content_crawler.spiders']
NEWSPIDER_MODULE = 'content_crawler.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 10

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'content_crawler.middlewares.DuplicateFilterMiddleware': 543,
}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'content_crawler.pipelines.DatabaseHandlerPipeline': 300,
}

# the sqlite or any other db info..
DATABASE = {
    'drivername': 'sqlite',
    # 'host': 'localhost',
    # 'port': '5432',
    # 'username': 'YOUR_USERNAME',
    # 'password': 'YOUR_PASSWORD',
    'database': 'ubuntu_forums.sqlite'
}
