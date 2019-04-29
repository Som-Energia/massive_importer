from .base import *


TASKS = {
    'check_new_events': tasks_conf['check_new_events']
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
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': massive_importer_conf.get('log_dir', False) or 'log/masive_importer.log',
            'when': 'midnight',
            'backupCount': 7,
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'massive_importer': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}
