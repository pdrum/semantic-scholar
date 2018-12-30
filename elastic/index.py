import json

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


def read_iterate():
    with open('../crawl/crawl.json') as file:
        data = json.load(file)
        for paper in data:
            yield {
                '_index': 'semanticscholar',
                '_type': 'paper',
                'doc': paper
            }


def build_index():
    es = Elasticsearch()
    bulk(es, read_iterate())


if __name__ == '__main__':
    build_index()
