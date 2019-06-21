# -*- coding: utf-8 -*-
import logging, time, urllib, threading, datetime
import concurrent.futures
from multiprocessing import Process
from datetime import datetime, date, timedelta
from massive_importer.crawlers.run_crawlers import WebCrawler
from massive_importer.lib.minio_utils import MinioManager
from massive_importer.lib.alert_utils import AlertManager
from massive_importer.lib.erp_utils import ErpManager
from massive_importer.lib.db_utils import listEvents, listImportFiles, listImportFiles_by_date_interval, updateState, eventToImportFile
from massive_importer.conf import configure_logging, settings
from massive_importer.models.importer import Event, ImportFile, UpdateStatus
from pony.orm import select, db_session, delete


logger = logging.getLogger(__name__)
minio_manager = MinioManager(**settings.MINIO)
erp_manager = ErpManager(**settings.ERP)
alert_manager = AlertManager(**settings.MAIL)
mutex = threading.Lock()

MAX_NUM_RETRIES = 3

def web_crawling():
    logger.debug("Crawl process starting... ")
    wc = WebCrawler().crawl()
    logger.debug("Crawl process done!")
    
@db_session(optimistic=False) 
def check_new_events(impfs = None): 
    if erp_manager == None : 
        raise ValueError("There is no ERP Connection") 
    logger.debug("Import zips process stating...") 

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
                    logger.debug('%s generated with result: %r' % (event.name, res)) 
    else: logger.debug("No ImportFiles pending")                    
    logger.debug("Process done!")

@db_session
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
                    updateState(impf, UpdateStatus.ERROR)
                else:
                    impf.retries = impf.retries +1
                    import_zips(impf)
            else:       
                updateState(impf, UpdateStatus.FINISHED) 
                return True 
        except Exception as e: 
            msg = "An error ocurred importing %s: %s" 
            logger.exception(msg, impf.name, str(e))

@db_session
def summary():
    today = date.today()
    i_date = datetime(today.year, today.month, today.day, 0, 0, 0)
    f_date = i_date + timedelta(days=1)
    events = listEvents()
    impfs = listImportFiles_by_date_interval(i_date, f_date)
    alert_manager.summary_send(i_date, f_date, events, impfs)