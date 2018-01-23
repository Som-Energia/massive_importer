# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from apscheduler.executors.pool import ThreadPoolExecutor

from .base import *


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
    'database': 'massive_importer_db',
    'user': 'massive_importer',
    'password': '1234'
}

ERP = {
    'server': '',
    'db': '',
    'user': '',
    'password': ''
}

EXECUTORS = {
    'default': ThreadPoolExecutor(max_workers=10)
}

TASKS = {
    'import_zips': {
        'trigger': 'interval',
        'minutes': 1,
        'next_run_time': datetime.now() + timedelta(seconds=20)
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
