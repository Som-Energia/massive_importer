# -*- coding: utf-8 -*-
from .base import *
from datetime import datetime, timedelta
from apscheduler.executors.pool import ThreadPoolExecutor

CRAWLERS = crawlers_conf


MINIO = {
    'endpoint': 'localhost:9000',
    'access_key': '',
    'secret_key': '',
    'secure': True
}

DATABASE = {
    'provider': 'postgres',
    'host': 'localhost',
    'port': 5432,
    'database': 'bucketevents_db',
    'user': 'postgres',
    'password': 'postgres'
}

ERP = {
    'server': erp_conf['server'],
    'db': erp_conf['db'],
    'user': erp_conf['user'],
    'password': erp_conf['password']
}

EXECUTORS = {
    'default': ThreadPoolExecutor(max_workers=10)
}

TASKS = {
    'check_new_events': {
        'trigger': 'interval',
        'minutes': 1000,
        'next_run_time': datetime.now() + timedelta(seconds=1000)
    },

    'web_crawling': {
        'trigger': 'interval',
        'minutes': 100,
        'next_run_time': datetime.now() + timedelta(seconds=5)
    }
}

MAIL = {
    'from_address': mail_conf['from_address'],
    'to_address': mail_conf['to_address'],
    'host': mail_conf['host'],
    'port': mail_conf['port'],
    'password': mail_conf['password']
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(process)d] [%(levelname)s]'
            '[%(module)s.%(funcName)s:%(lineno)s] %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'massive_importer': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'apscheduler': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'pony': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        }
    }

}
