# -*- coding: utf-8 -*-
import logging

from scrapy import signals
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, StaticPool

logger = logging.getLogger(__name__)
DeclarativeBase = declarative_base()


class Page(DeclarativeBase):
    """
    The pages table sqlalchemy class to be used by the sqlite pipeline..
    """
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    url = Column('url', String)
    content = Column('content', String)
    referer = Column('referer', String)

    def __repr__(self):
        return "<Page({})>".format(self.url)


class DatabaseHandlerPipeline(object):
    """
    The sqlite db handler pipeline used to process the page item
    to create a record in the db pages table..
    """

    def __init__(self, settings):
        self.database = settings.get('DATABASE')
        self.sessions = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(crawler.settings)
        return pipeline

    def create_engine(self):
        engine = create_engine(URL(**self.database), poolclass=StaticPool, echo=True,
                               connect_args={'check_same_thread': False}, )
        return engine

    def create_tables(self, engine):
        DeclarativeBase.metadata.create_all(engine, checkfirst=True)

    def create_session(self, engine):
        session = sessionmaker(bind=engine)()
        return session

    def open_spider(self, spider):
        engine = self.create_engine()
        self.create_tables(engine)
        session = self.create_session(engine)
        self.sessions[spider] = session

    def close_spider(self, spider):
        session = self.sessions.pop(spider)
        session.close()

    def process_item(self, item, spider):
        """
        Main function of the pipeline, processes the page item
        add to the db if it doesn't exist
        :param item: the page item to be added..
        :param spider: the running spider crawling the item
        :return: the page item for further processing
        """
        session = self.sessions[spider]
        page = Page(**item)
        link_exists = session.query(Page).filter_by(url=item['url']).first() is not None

        if link_exists:
            logger.info('Item {} is in db'.format(page))
            return item

        try:
            session.add(page)
            session.commit()
            logger.info('Item {} stored in db'.format(page))
        except:
            logger.info('Failed to add {} to db'.format(page))
            session.rollback()
            raise

        return item
