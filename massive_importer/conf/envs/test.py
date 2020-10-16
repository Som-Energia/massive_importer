from .base import *
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime, timedelta

ERP = erp_conf

SCRAPY_CRAWLERS = scrapy_crawlers_conf
SELENIUM_CRAWLERS = selenium_crawlers_conf

MAIL = {
    'from_address': mail_conf['from_address'],
    'to_address': mail_conf['to_address'],
    'host': mail_conf['host'],
    'port': mail_conf['port'],
    'password': mail_conf['password']
}

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
        'minutes': 1000000000,
        'next_run_time': datetime.now() + timedelta(seconds=10000000000)
    },

    'summary': {
        'trigger': 'interval',
        'minutes': 3,
        'next_run_time': datetime.now() + timedelta(seconds=60)
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
