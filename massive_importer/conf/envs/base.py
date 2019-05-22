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

crawlers_conf = massive_importer_conf['crawlers']
for item in crawlers_conf:
    crawlers_conf[item] = crawlers_conf[item] == 'True' 
    
# tasks_conf = massive_importer_conf['tasks']

TMP_DIR = os.path.join(BASE_DIR, 'tmp')
