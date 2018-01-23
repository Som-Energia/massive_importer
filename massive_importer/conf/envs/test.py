from .base import *


MINIO = {
    'endpoint': 'localhost:9000',
    'access_key': 'ZJXAA7MQOGXF01F0QKUH',
    'secret_key': 'GSEHnN2zDuMtbxtEc2vdXiaUbYs+tP2mdG45S5jK',
    'secure': False
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
