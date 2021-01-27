# -*- coding: utf-8 -*-
from .base import *
from datetime import datetime, timedelta
from apscheduler.executors.pool import ThreadPoolExecutor

SCRAPY_CRAWLERS = scrapy_crawlers_list
SELENIUM_CRAWLERS = selenium_crawlers_list

SCRAPY_CRAWLERS_CONF = scrapy_crawlers_conf
SELENIUM_CRAWLERS_CONF = selenium_crawlers_conf

MINIO = minio_conf
MAIL = mail_conf
DATABASE = database_conf
ERP = erp_conf

EXECUTORS = {
    'default': ThreadPoolExecutor(max_workers=10)
}

TASKS = {
    'web_crawling': {
        'trigger': 'cron',
        'hour': 21,
        'minutes': 0,
    },

    'check_new_events': {
        'trigger': 'cron',
        'hour': 22,
        'minute': 0,
    },

    'summary': {
        'trigger': 'cron',
        'hour': 23,
        'minutes': 30,
    }
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
