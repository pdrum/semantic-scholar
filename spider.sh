#!/usr/bin/env bash

cd crawl
scrapy runspider spider.py -o crawl.json
