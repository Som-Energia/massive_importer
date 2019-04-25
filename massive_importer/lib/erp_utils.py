import logging
from erppeek import Client
import base64
import os


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
        return base64.encodebytes(content).decode()

    def import_wizard(self, file_name, file_content, mutex):
        values = {'filename': file_name, 'file': self.get_file_b64content(file_content)}
        mutex.acquire()
        WizardImportAtrF1 = self.erp_client.model('wizard.import.atr.and.f1')
        import_wizard = WizardImportAtrF1.create(values)
        context = {'active_ids': [import_wizard.id], 'active_id': import_wizard.id}         
        try:  
            res = import_wizard.action_import_xmls(context)
        except Exception as e:
            msg = "An error ocurred importing %s: %s"
            logger.exception(msg, file_name, str(e))
            result = False
        else:
            result = True
            
        mutex.release()
        return result
