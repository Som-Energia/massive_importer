from .base import *
from apscheduler.executors.pool import ThreadPoolExecutor


MINIO = {
    'endpoint': 'localhost:9000',
    'access_key': 'NJHXYRAAILTKUVSXWDP9',
    'secret_key': 'IqoH+bHYxkfE8xvmLpMdaxjLGJkmhria3Qxi9Q73',
    'secure': False
}

DATABASE = {
    'provider': 'postgres',
    'host': 'localhost',
    'port': 5432,
    'database': 'test_importer',
    'user': 'postgres',
    'password': 'postgres'
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
