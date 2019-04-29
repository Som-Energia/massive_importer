# -*- coding: utf-8 -*-
import logging
from massive_importer.lib.minio_utils import MinioManager
from massive_importer.lib.alert_utils import AlertManager
from massive_importer.lib.erp_utils import ErpManager
from massive_importer.lib.db_utils import listEvents, updateState, eventToImportFile
from massive_importer.conf import configure_logging, settings
from massive_importer.models.importer import Event, ImportFile, UpdateStatus
from pony.orm import select, db_session, delete
import concurrent.futures
from multiprocessing import Process
import time
import urllib
import threading

logger = logging.getLogger(__name__)
minio_manager = MinioManager(**settings.MINIO)
erp_manager = ErpManager(**settings.ERP)
alert_manager = AlertManager(**settings.MAIL)
mutex = threading.Lock()

MAX_NUM_RETRIES = 3

@db_session(optimistic=False) 
def check_new_events(impfs = None): 
    if erp_manager == None : 
        raise ValueError("There is no ERP Connection") 
    logger.debug("***Importando zips!***") 

    if impfs is None:
        impfs = []
        eventList = listEvents() 
        if eventList:          
            for event in eventList: 
                impf = eventToImportFile(event) 
                if impf: 
                    impfs.append(impf) 
                    logger.debug('Afegit l\'ImportFile %s a la llista!' % urllib.parse.unquote(impf.name)) 
                    event.delete()
        else: logger.debug("No Events pending")
    
    if impfs:                  
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor: 
            future_to_events = {executor.submit(import_zips, impf): impf for impf in impfs}     
            for future in concurrent.futures.as_completed(future_to_events): 
                event = future_to_events[future] 
                try: 
                    res = future.result() 
                except Exception as e:
                    msg = "%r generated an exception: %s"
                    logger.exception(msg, event, str(e)) 
                else: 
                        print('%s generated with result: %r' % (event, res)) 
    else: logger.debug("No ImportFiles pending")                    
    logger.debug("***Ya he terminado :)***")

def import_zips(impf):
    updateState(impf, UpdateStatus.IN_PROCESS) 
    content = None 
    try: 
        content = minio_manager.get_file_content(impf.bucket, urllib.parse.unquote(impf.name)) 
    except Exception as e: 
        updateState(impf, UpdateStatus.ERROR) 
        msg = "Error getting file content from Minio bucket, generated an exception: %s" 
        logger.exception(msg, impf.name, str(e)) 
    else: 
        try:
            res = erp_manager.import_wizard(impf.name, content, mutex)
            if not res:
                if impf.retries >= MAX_NUM_RETRIES:
                    alert_manager.alert_send(missatge="No s'ha pogut pujar el següent fitxer:", llistat=[impf.name])
                    updateState(impf, UpdateStatus.ERROR)
                else:
                    impf.retries = impf.retries +1
                    check_new_events(impfs=[impf])
            else:       
                updateState(impf, UpdateStatus.FINISHED) 
                return True 
        except Exception as e: 
            msg = "An error ocurred importing %s: %s" 
            logger.exception(msg, impf.name, str(e))
