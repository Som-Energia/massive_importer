import logging
from erppeek import Client
import base64
import os
from massive_importer.lib.exceptions import InvalidEncodingException

logger = logging.getLogger(__name__)

class ErpManager(object):
    def __init__(self, server, db, user, password, verbose=False):     
        self.erp_client = Client(
            server=server,
            db=db,
            user=user,
            password=password,
            verbose=verbose
        )
    
    def get_file_b64content(self, content):
        try:
            return base64.encodebytes(content).decode()
        except Exception as e:
            raise InvalidEncodingException('Content must be b64 encoded.')

    def import_wizard(self, file_name, file_content, mutex=None):
        if file_name.endswith('.zip'):
            values = {'filename': file_name, 'file': self.get_file_b64content(file_content)}
            if mutex is not None:
                mutex.acquire()
            WizardImportAtrF1 = self.erp_client.model('wizard.import.atr.and.f1')
            import_wizard = WizardImportAtrF1.create(values)
            context = {'active_ids': [import_wizard.id], 'active_id': import_wizard.id}         
            try:  
                res = import_wizard.action_import_xmls(context)
                return (import_wizard.state == 'done' or import_wizard.state == 'load')
            except Exception as e:
                msg = "An error ocurred importing %s: %s"
                logger.exception(msg, file_name, str(e))
                result = False
            else:
                result = True
            finally:
                if mutex is not None:    
                    mutex.release()
        else: return False

class MockErpManager(object):
    def import_wizard(self, file_name, file_content):
        return False
