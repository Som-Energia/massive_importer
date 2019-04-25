import base64
import os
from unittest import TestCase

from erppeek import Client

os.environ.setdefault('MASSIVE_IMPORTER_SETTINGS', 'massive_importer.conf.envs.devel')

from massive_importer.conf import settings
from massive_importer.lib import ErpManager

DATA_DIR = os.path.join(settings.BASE_DIR, 'tests/data')

class TestErpManager(TestCase):

    def setUp(self):
        self.erp_manager = ErpManager(**settings.ERP)

    def get_file_b64content(self):
        with open(os.path.join(DATA_DIR, 'prova.zip'), 'rb') as f:
            file_content = f.read()
        return base64.encodebytes(file_content).decode()


    def test_import_wizard(self):
        file_name = 'test_filename'
        file_content = get_file_b64content

        values = {'file': file_content, 'filename' : file_name}
        WizardImportAtrF1 = self.erp_client.model('wizard.import.atr.and.f1')
        import_wizard = WizardImportAtrF1.create(values)
        
        context = {'active_ids': [import_wizard.id], 'active_id': import_wizard.id}         
        res = import_wizard.action_import_xmls(context)
        self.assertTrue(res)
        self.assertTrue(import_wizard.state == 'done' or import_wizard.state == 'load' )


