from bs4 import BeautifulSoup
from time import strftime

import re
import requests
import logging


def _check_if_element_exists(element):
    if element is not None:
        return element.text.replace('\n', '')
    else:
        return None


class SpiegelCrawler:
    def __init__(self, url):
        self.url = url
        self.current_crawling_timestamp = None

    def crawl(self):
        self._update_timestamp()
        logging.info('New crawling started at: ', self.current_crawling_timestamp)

        articles = self._get_page_articles()
        if len(articles) > 0:
            logging.info('Number of articles found: %i' % len(articles))
        else:
            logging.warning('0 articles found at the webpage')

        parsed_data = [self._parse_article(a) for a in articles]
        return parsed_data

    def _update_timestamp(self):
        self.current_crawling_timestamp = strftime("%Y-%m-%d %H:%M:%S")

    def _get_page_articles(self):
        page_content = requests.get(self.url)
        page = BeautifulSoup(page_content.text, "lxml")
        return page.findAll('article')

    def _parse_article(self, art):
        link = art.find('a')['href']

        abstract = art.find('section')
        abstract_text = _check_if_element_exists(abstract)

        reg = re.compile('.*focus:text-primary-darker.*')
        header = art.find('span', attrs={'class': reg})
        header_text = _check_if_element_exists(header)

        title_text = art['aria-label']

        return {'id': link,
                'source': {'title': title_text,
                           'header': header_text,
                           'abstract': abstract_text,
                           'org-time': self.current_crawling_timestamp,
                           'update-time': self.current_crawling_timestamp}}
