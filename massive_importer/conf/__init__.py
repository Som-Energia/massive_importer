# -*- coding: utf-8 -*-
import os
from importlib import import_module
from massive_importer.lib.exceptions import ImproperlyConfigured

ENVIRONMENT_VARIABLE = 'MASSIVE_IMPORTER_SETTINGS'

os.environ.setdefault('MASSIVE_IMPORTER_SETTINGS', 'massive_importer.conf.envs.test')

class Settings(object):
    ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

    def __init__(self, settings_module):
        self.SETTINGS_MODULE = settings_module
        if not self.SETTINGS_MODULE:
            msg = 'Environment variable \"{}\" is not set'
            raise ImproperlyConfigured(msg.format(ENVIRONMENT_VARIABLE))

        mod = import_module(self.SETTINGS_MODULE)
        for setting in dir(mod):
            if setting.isupper():
                setattr(self, setting, getattr(mod, setting))
        self.DEBUG_MODE = False

settings = Settings(os.getenv(ENVIRONMENT_VARIABLE))

def configure_logging(logging_config):
    from logging.config import dictConfig

    dictConfig(logging_config)
