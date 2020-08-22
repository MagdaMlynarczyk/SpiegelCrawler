import logging
import sys

from elasticsearch import helpers, Elasticsearch
from elasticsearch.exceptions import ConnectionError, ConnectionTimeout


def create_index(es, name):
    """Create index in Elasticsearch database if it does not exist

    :param
        es (elasticsearch.client.Elasticsearch): the instance of the Elasticsearch class
        name (str): name of an index to be created
    """
    if not es.indices.exists(name):
        es.indices.create(name)
        logging.info("Index %s created" % name)
    else:
        logging.info("Index %s already exists" % name)


class ElasticConnector:
    """A connector to the Elasticsearch database
    :param
        es_path (str): path to the Elasticsearch database
        index (str): name of the index of interest
    """
    def __init__(self, es_path, index_name):
        self.path = es_path
        self.index = index_name

        try:
            self.es = Elasticsearch(es_path)
            logging.info('Connected to Elasticsearch')
        except (ConnectionError, ConnectionTimeout):
            logging.critical('Could not connected to Elasticsearch, aborting')
            sys.exit(1)

        # create the index if it doesn't exist
        create_index(self.es, self.index)

    def _prep_article(self, art):
        """Parse article to the database data model

        :param
            art (dict): an element of output list of SpiegelCrawler.crawl() methods
        """
        return {'_index': self.index,
                '_type': '_doc',
                '_id': art['id'],
                '_source': art['source']}

    def _check_duplicate(self, article_id):
        """Check if an article with given id is already saved in database

        :return boolean: True if the article is already saved in the database
        """
        return self.es.exists(
            index='spiegel-international-news',
            doc_type='_doc',
            id=article_id)

    def _update_article(self, art):
        """Set article update-time atrribute to the current crawling timestamp

        :param
            art (dict): an element of output list of SpiegelCrawler.crawl() method
        """
        self.es.update(index=self.index,
                       doc_type='_doc',
                       id=art['id'],
                       body={'doc': {'update-time': art['source']['org-time']}})

    def _handle_one_article(self, art):
        """Check if the article has already been saved in database and save it or update

        :param
            art (dict): an element of output list of SpiegelCrawler.crawl() method
        """
        if self._check_duplicate(art['id']):
            self._update_article(art)
            return 'updated'
        else:
            helpers.bulk(self.es, [self._prep_article(art)])
            return 'new'


    def save_data(self, articles):
        """Load data to the database for all articles

        :param
            articles (list): Output of SpiegelCrawler.crawl() method"""
        new_articles = 0
        for art in articles:
            res = self._handle_one_article(art)
            if res == 'new':
                new_articles += 1

        logging.info('%d new articles' % new_articles)