import re
import requests
import logging

from bs4 import BeautifulSoup
from time import strftime


def _prep_element(element):
    """Check if an html element is not None and extract text from it"""
    if element is not None:
        return element.text.replace('\n', '')
    else:
        return None


class SpiegelCrawler:
    """Crawl articles metadata from Spiegel website - International bookmark

    :param:
        url (str): url to crawl
    """
    def __init__(self, url):
        self.url = url
        self.current_crawling_timestamp = None

    def crawl(self):
        """Crawl and parse relevant information from given url

        :return: list: List of dictionaries, one dictionary responds to one crawled article and
        is an output of the _parse_article method
        """
        self._update_timestamp()
        logging.info('New crawling started at: %s' % self.current_crawling_timestamp)

        articles = self._get_page_articles()
        if len(articles) > 0:
            logging.info('Crawled %d articles' % len(articles))
        else:
            logging.warning('0 articles found at the webpage')

        parsed_data = [self._parse_article(a) for a in articles]
        return parsed_data

    def _update_timestamp(self):
        """Set timestamp for current crawling run"""
        self.current_crawling_timestamp = strftime("%Y-%m-%d %H:%M:%S")

    def _get_page_articles(self):
        """Crawl the page from the url and find articles"""
        page_content = requests.get(self.url)
        page = BeautifulSoup(page_content.text, "lxml")
        return page.findAll('article')

    def _parse_article(self, art):
        """Extract relevant information from source article

        :param
            art (bs4.element.Tag): part of the html containing data about one article

        :return dict: The dictionary keys are:
            id (str): link to the article
            source (dict): metadata of the article. A dictionary with keys:
                title (str): title of the article
                header (str): header of the article
                abstract (str): abstract of the article
                orig-time (str): timestamp current crawling of the article
                update-time (str): the same as orig-timestamp
        """
        link = art.find('a')['href']

        abstract = art.find('section')
        abstract_text = _prep_element(abstract)

        reg = re.compile('.*focus:text-primary-darker.*')
        header = art.find('span', attrs={'class': reg})
        header_text = _prep_element(header)

        title_text = art['aria-label']

        return {'id': link,
                'source': {'title': title_text,
                           'header': header_text,
                           'abstract': abstract_text,
                           'org-time': self.current_crawling_timestamp,
                           'update-time': self.current_crawling_timestamp}}
