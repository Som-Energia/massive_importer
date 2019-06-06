# -*- coding: utf-8 -*-
from .base import *
from datetime import datetime, timedelta
from apscheduler.executors.pool import ThreadPoolExecutor

CRAWLERS = crawlers_conf

MINIO = minio_conf

DATABASE = {
    'provider': database_conf['provider'],
    'host': database_conf['host'],
    'port': database_conf['port'],
    'database': database_conf['database'],
    'user': database_conf['user'],
    'password': database_conf['password'],
}

ERP = {
    'server': erp_conf['server'],
    'db': erp_conf['db'],
    'user': erp_conf['user'],
    'password': erp_conf['password'],
}

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
