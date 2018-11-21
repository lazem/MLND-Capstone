from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, StaticPool

DeclarativeBase = declarative_base()


class Page(DeclarativeBase):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    url = Column('url', String)
    content = Column('content', String)
    content_text = Column('content_text', String)
    referer = Column('referer', String)

    def __repr__(self):
        return "<Page({})>".format(self.url)


class UrlsScore(DeclarativeBase):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True)
    url1 = Column('url1', String)
    url2 = Column('url2', String)
    struct_score = Column('struct_score', Float)
    sem_score = Column('sem_score', Float)
    score = Column('score', Float)

    def __repr__(self):
        return "<Page({})>".format(self.score)


class Referer(DeclarativeBase):
    __tablename__ = "referers"

    id = Column(Integer, primary_key=True)
    url = Column('url', String)
    done = Column('done', Boolean)


class DatabaseHandler(object):
    """
    The db handler class for processing the crawled db,
    and turn it into a training set..
    """
    def __init__(self):
        self.database = {
            'drivername': 'sqlite',
            # 'host': 'localhost',
            # 'port': '5432',
            # 'username': 'YOUR_USERNAME',
            # 'password': 'YOUR_PASSWORD',
            'database': 'ubuntu.sqlite'
        }
        self.sessions = {}
        self.engine = self.create_engine()
        self.create_tables(self.engine)
        self.session = self.create_session(self.engine)

    def create_engine(self):
        engine = create_engine(URL(**self.database), poolclass=StaticPool, echo=True,
                               connect_args={'check_same_thread': False}, )
        return engine

    def create_tables(self, engine):
        DeclarativeBase.metadata.create_all(engine, checkfirst=True)

    def create_session(self, engine):
        session = sessionmaker(bind=engine)()
        return session

    def find_content(self, url):
        page = self.session.query(Page).filter_by(url=b'%s'.decode('utf8') % url).first()
        if not page and type(url) != str:
            page = self.session.query(Page).filter_by(url=url.decode('utf8')).first()
        if not page:
            return "", ""
        return b'%s'.decode('utf8') % page.content, b'%s'.decode('utf8') % page.content_text

    def find_urls_by_referer(self, referer):
        pages = self.session.query(Page).filter_by(referer=referer)
        return [page.url for page in pages]

    def find_distinct(self):
        referes = []
        for value in self.session.query(Page.referer).distinct():
            referes.append(Referer(url=value[0]))
            if len(referes) == 100:
                self.session.bulk_save_objects(referes)
                self.session.commit()
                referes = []

    def find_referer(self):
        return self.session.query(Referer).filter_by(done=None).first()

    def update_referer(self, referer):
        referer.done = True
        self.session.commit()

    def add_url_pair(self, pairs):

        self.session.bulk_save_objects(pairs)
        self.session.commit()

    def add_column(self):
        column = Column('content_text', String)
        column_name = column.compile(dialect=self.engine.dialect)
        column_type = column.type.compile(self.engine.dialect)
        self.engine.execute('ALTER TABLE %s ADD COLUMN %s %s' % ("pages", column_name, column_type))
        # self.session.commit()

    def update_content_text(self, remover_boiler_code):
        pages = []
        for page in self.session.query(Page):
            page.content_text = remover_boiler_code(str(page.content))
            pages.append(page)
            # self.session.commit()
            if len(pages) == 1000:
                self.session.bulk_save_objects(pages)
                self.session.commit()
                pages = []

    def update_sim_score(self, stuct_func, sem_func):
        '''
        Find similarity score for each url pair
        :param stuct_func: structural similarity function to use
        :param sem_func: semantic similarity function to us
        :return:
        '''
        url_scores = []
        for url_score in self.session.query(UrlsScore):
            html1, str1 = self.find_content(url_score.url1)
            html2, str2 = self.find_content(url_score.url2)
            # ignore empty or xml files
            if html1 == "" or html2 == "" or '<?xml version="1.0"' in html1 or '<?xml version="1.0"' in html2:
                continue

            struct_score = stuct_func(html1, html2)
            if not str1 or not str2:
                str1 = html1
                str2 = html2
            sem_score = sem_func(str1, str2)
            url_score.struct_score = struct_score
            url_score.sem_score = sem_score
            url_score.score = (sem_score + struct_score) / 2

            url_scores.append(url_score)
            if len(url_scores) == 1000:
                self.session.bulk_save_objects(url_scores)
                self.session.commit()
                url_scores = []
