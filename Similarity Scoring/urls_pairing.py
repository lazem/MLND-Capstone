import itertools
from db_handler import UrlsScore


def all_pairs(lst):
    '''
    Get all combinations of the url list
    :param lst: all the referes and their urls
    :return: combination generator
    '''
    for p in itertools.combinations(lst, 2):
        i = iter(p)
        yield zip(i, i)


def fill_url_pairs(db_handler):
    '''
    Get each referer and its urls, make url pairs for their combinations
    :param db_handler: the database handler
    :return:
    '''
    while True:
        referer = db_handler.find_referer()
        if not referer:
            break
        urls = db_handler.find_urls_by_referer(referer.url)
        if referer.url:
            urls.append(referer.url)
        pairs = []
        for x in all_pairs(urls):
            for pair in x:
                pairs.append(UrlsScore(url1=pair[0], url2=pair[1]))
        if pairs:
            db_handler.add_url_pair(pairs)
        db_handler.update_referer(referer)
