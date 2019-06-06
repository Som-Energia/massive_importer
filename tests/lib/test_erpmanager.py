import base64
import os, logging
from unittest import TestCase
from erppeek import Client
os.environ.setdefault('MASSIVE_IMPORTER_SETTINGS', 'massive_importer.conf.envs.test')
from massive_importer.conf import settings
from massive_importer.lib.erp_utils import ErpManager
logger = logging.getLogger(__name__)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/')


class TestErpManager(TestCase):

    def setUp(self):
        self.erp_client = Client(**settings.ERP, verbose=False)

    def get_file_b64content(self):
        logger.error(os.path.join(DATA_DIR, 'prova.zip'))
        with open(os.path.join(DATA_DIR, 'prova.zip'), 'rb') as f:
            file_content = f.read()
        return base64.encodebytes(file_content).decode()

    def test_import_wizard(self):
        file_name = 'test_filename'
        file_content = self.get_file_b64content()

        values = {'file': file_content, 'filename' : file_name}
        WizardImportAtrF1 = self.erp_client.model('wizard.import.atr.and.f1')
        import_wizard = WizardImportAtrF1.create(values)
        
        context = {'active_ids': [import_wizard.id], 'active_id': import_wizard.id}         
        res = import_wizard.action_import_xmls(context)
        self.assertTrue(res)
        self.assertTrue(import_wizard.state == 'done' or import_wizard.state == 'load' )


