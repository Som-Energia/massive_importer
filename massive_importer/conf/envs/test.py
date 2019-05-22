from .base import *
from apscheduler.executors.pool import ThreadPoolExecutor

CRAWLERS = crawlers_conf

MINIO = {
    'default_bucket': minio_conf['default_bucket'],
    'endpoint': minio_conf['endpoint'],
    'access_key': minio_conf['access_key'],
    'secret_key': minio_conf['secret_key'],
    'secure': minio_conf['secure']
}

ERP = {
    'server': erp_conf['server'],
    'db': erp_conf['db'],
    'user': erp_conf['user'],
    'password': erp_conf['password']
}

DATABASE = {
    'provider': 'postgres',
    'host': database_conf['host'],
    'port': database_conf['port'],
    'database': database_conf['database'],
    'user': database_conf['user'],
    'password': database_conf['password']
}

EXECUTORS = {
    'default': ThreadPoolExecutor(max_workers=10)
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
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'log/masive_importer.log',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'massive_importer': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

MAIL = {
    'from_address': mail_conf['from_address'],
    'to_address': mail_conf['to_address'],
    'host': mail_conf['host'],
    'port': mail_conf['port'],
    'password': mail_conf['password']
}