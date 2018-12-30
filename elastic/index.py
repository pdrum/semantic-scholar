import json
import os

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


def read_iterate():
    pwd = os.path.dirname(__file__)
    root = os.path.dirname(pwd)
    with open(root + '/crawl/crawl.json') as file:
        data = json.load(file)
        for paper in data:
            yield {
                '_index': 'paper_index',
                '_type': 'paper',
                'doc': paper
            }


def build_index():
    es = Elasticsearch()
    bulk(es, read_iterate())


def delete_index():
    es = Elasticsearch()
    es.indices.delete(index='paper_index', ignore=[400, 404])
