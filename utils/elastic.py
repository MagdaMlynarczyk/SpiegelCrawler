from elasticsearch import helpers, Elasticsearch
from elasticsearch.exceptions import ConnectionError, ConnectionTimeout
import logging
import sys


def create_index(es, name):
    if not es.indices.exists(name):
        es.indices.create(name)
        logging.info("Index %s created" % name)
    else:
        logging.info("Index %s already exists" % name)


class ElasticConnector:
    def __init__(self, es_path, index_name):
        self.path = es_path
        self.index = index_name

        try:
            self.es = Elasticsearch(es_path)
            logging.info('Connected to Elasticsearch')
        except (ConnectionError, ConnectionTimeout):
            logging.critical('Could not connected to Elasticsearch, aborting')
            sys.exit(1)

        create_index(self.es, self.index)

    def _prep_article(self, art):
        return {'_index': self.index,
                '_type': '_doc',
                '_id': art['id'],
                '_source': art['source']}

    def _check_duplicate(self, article_id):
        return self.es.exists(
            index='spiegel-international-news',
            doc_type='_doc',
            id=article_id)

    def _update_article(self, art):
        self.es.update(index=self.index,
                       doc_type='_doc',
                       id=art['id'],
                       body={'doc': {'update-time': art['source']['org-time']}})

    def _handle_one_article(self, art):
        if self._check_duplicate(art['id']):
            self._update_article(art)
        else:
            helpers.bulk(self.es, [self._prep_article(art)])

    def save_data(self, articles):
        for art in articles:
            self._handle_one_article(art)
