# -*- coding: utf-8 -*-
import os
import yaml

from massive_importer.lib.exceptions import ImproperlyConfigured

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

try:
    with open(os.path.join(BASE_DIR, 'massive_importer/conf/config.yaml')) as f:
        massive_importer_conf = yaml.load(f.read())
except Exception as e:
    raise ImproperlyConfigured(str(e))

minio_conf = massive_importer_conf['minio']

database_conf = massive_importer_conf['database']

erp_conf = massive_importer_conf['erp']

mail_conf = massive_importer_conf['mail']

scrapy_crawlers_conf = {}
selenium_crawlers_conf = {}

scrapy_crawlers_list = []
selenium_crawlers_list = []

for item in massive_importer_conf['crawlers']:
    crawler_info = massive_importer_conf['crawlers'][item]
    if crawler_info["crawler"] == 'Scrapy':
        scrapy_crawlers_conf[item] = crawler_info
        scrapy_crawler_list.append(item)
    if crawler_info["crawler"] == 'Selenium':
        selenium_crawlers_conf[item] = crawler_info
        selenium_crawlers_list.append(item)
# tasks_conf = massive_importer_conf['tasks']

TMP_DIR = os.path.join(BASE_DIR, 'tmp')
