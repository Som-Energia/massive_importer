import base64
import os, logging
from unittest import TestCase
from erppeek import Client
os.environ.setdefault('MASSIVE_IMPORTER_SETTINGS', 'massive_importer.conf.envs.test')
from massive_importer.conf import settings
from massive_importer.lib.erp_utils import ErpManager
from massive_importer.lib.exceptions import InvalidEncodingException

from .testhelper import TestHelper
testhelper = TestHelper()
logger = logging.getLogger(__name__)

class TestErpManager(TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.erp_client = ErpManager(**settings.ERP, verbose=False)

    def test_get_file_b64content(self):
        try:
            content = testhelper.get_content()
            self.erp_client.get_file_b64content(content)
        except InvalidEncodingException as e:
            self.fail(e)
        
        # bad encoding test
        content =  'this is a simple string for testing'
        with self.assertRaises(InvalidEncodingException) as context:
            self.erp_client.get_file_b64content(content)
            self.assertTrue('b64 encoded' in context.exception)
        
    def test_import_wizard(self):
        file_name = 'test_filename.zip'
        file_content = testhelper.get_content()

        ret = self.erp_client.import_wizard(file_name, file_content)
        self.assertTrue(ret)

        bad_file_content = testhelper.get_bad_content()
        ret2 = self.erp_client.import_wizard(file_name, bad_file_content)
        self.assertTrue(ret2) # Wizzard accepts any file...

    @classmethod
    def tearDownClass(cls):
        testhelper.disconnect_db()

