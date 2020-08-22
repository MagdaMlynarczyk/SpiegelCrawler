import datetime
import logging.config

from flask import Flask
from config import config
from apscheduler.schedulers.background import BackgroundScheduler

from utils.elastic import ElasticConnector
from utils.crawler import SpiegelCrawler


logging.basicConfig()
logging.config.dictConfig(config['logging'])

ec = ElasticConnector(
    es_path=config['elasticsearch']['path'],
    index_name=config['elasticsearch']['index'])

cs = SpiegelCrawler(
    url=config['url'])


def run_crawler():
    """Defines a function to be scheduled"""
    data = cs.crawl()
    ec.save_data(data)
    return


bs = BackgroundScheduler()
bs.add_job(
    run_crawler,
    'interval',
    minutes=config['time_interval_min'],
    next_run_time=datetime.datetime.now())
bs.start()

app = Flask(__name__)

if __name__ == '__main__':
    app.run()
