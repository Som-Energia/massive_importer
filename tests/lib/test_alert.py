import logging, os, sys, json
from datetime import datetime
from unittest import TestCase
from massive_importer.models.importer import Event, ImportFile, UpdateStatus, db
from massive_importer.conf import settings
from massive_importer.lib.alert_utils import AlertManager
from massive_importer.lib.exceptions import TooFewArgumentsException
os.environ.setdefault('MASSIVE_IMPORTER_SETTINGS', 'massive_importer.conf.envs.test')

from .testhelper import TestHelper
logger = logging.getLogger(__name__)
testhelper = TestHelper()
class AlertTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.alert_manager = AlertManager(**settings.MAIL)
        stream_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(stream_handler)

    def test_alert_send(self):
        #simple alarm test msg + list
        llistat = ['element1','element2','element3']
        self.assertTrue(self.alert_manager.alert_send('Test message', llistat))
        
    def test_summary_send_full(self):
        #fullfilled summary
        summary = testhelper.create_summary()
        self.assertTrue(self.alert_manager.summary_send(**summary))

    def test_summary_send_no_dates(self): 
        #summary with no dates -> Error
        summary = testhelper.create_summary(no_dates=True)
        with self.assertRaises(TooFewArgumentsException) as context:
            self.alert_manager.summary_send(**summary)
            self.assertTrue('dates missig' in context.exception)

    def tearDown(self):
        testhelper.clean_tables()
    
    @classmethod
    def tearDownClass(cls):
        cls.alert_manager.close()
        testhelper.disconnect_db()
