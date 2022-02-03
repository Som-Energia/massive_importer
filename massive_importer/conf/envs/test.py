from .base import *
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime, timedelta

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
    'check_new_events': {
        'trigger': 'interval',
        'minutes': 1,
        'next_run_time': datetime.now() + timedelta(seconds=5)
    },
    'web_crawling': {
        'trigger': 'interval',
        'minutes': 10000,
        'next_run_time': datetime.now() + timedelta(seconds=5)
    },
    'summary': {
        'trigger': 'interval',
        'minutes': 3,
        'next_run_time': datetime.now() + timedelta(seconds=500000)
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
