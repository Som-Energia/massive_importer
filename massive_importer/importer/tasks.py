# -*- coding: utf-8 -*-
import logging, time, urllib, threading
import concurrent.futures
from multiprocessing import Process
from datetime import datetime, date, timedelta
from massive_importer.crawlers.run_crawlers import WebCrawler
from massive_importer.lib.minio_utils import MinioManager
from massive_importer.lib.alert_utils import AlertManager
from massive_importer.lib.erp_utils import ErpManager
from massive_importer.lib.db_utils import delete_events, checkEtag, listEvents, listImportFiles, listCrawlingProcessErrors_by_date_interval, listImportFiles_by_date_interval, updateState, eventToImportFile
from massive_importer.conf import configure_logging, settings
from massive_importer.models.importer import Event, ImportFile, UpdateStatus
from pony.orm import select, db_session, delete
logger = logging.getLogger(__name__)

class Tasks:
    def __init__(self, erp_manager=None, web_crawler=None):
        self.minio_manager = MinioManager(**settings.MINIO)
        self.erp_manager = ErpManager(**settings.ERP) if  erp_manager is None else erp_manager
        self.wc = WebCrawler() if web_crawler is None else web_crawler
        self.date_download_task = None
        self.date_events_task = None
        self.mutex = threading.Lock()
        self.downloaded_list = {}

    def web_crawling(self):
        logger.debug("Crawl process starting... ")
        self.wc.crawl()
        logger.debug("Crawl process done!")
        self.wc.check_downloaded_files()
        self.downloaded_list = self.wc.done_list
        self.date_download_task = datetime.now()

    @db_session(optimistic=False)
    def check_new_events(self, impfs = None):
        if self.erp_manager == None :
            raise ValueError("There is no ERP Connection")
        logger.debug("Import zips process stating...")
        eventList = []
        if impfs is None:
            impfs = []
            eventList = listEvents()
            if eventList:
                for event in eventList:
                    impf = None if checkEtag(event) else eventToImportFile(event)
                    if impf:
                        impfs.append(impf)
                        logger.debug('Afegit l\'ImportFile %s a la llista!' % urllib.parse.unquote_plus(impf.name))
                    else:
                        logger.error('L\'arxiu %s ja ha estat importat, es descarta!' % event)
            else: logger.debug("No Events pending")

        if impfs:
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                future_to_events = {executor.submit(self.import_zips, impf): impf for impf in impfs}
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
        delete_events(eventList)
        self.date_events_task = datetime.now()

    @db_session
    def import_zips(self, impf):
        updateState(impf, UpdateStatus.IN_PROCESS)
        content = None
        try:
            content = self.minio_manager.get_file_content(impf.bucket, urllib.parse.unquote_plus(impf.name))
        except Exception as e:
            updateState(impf, UpdateStatus.ERROR)
            msg = "Error getting file content from Minio bucket, generated an exception: %s"
            logger.exception(msg, impf.name, str(e))
        else:
            try:
                res = self.erp_manager.import_wizard(urllib.parse.unquote_plus(impf.name), content, self.mutex)
                if not res:
                    updateState(impf, UpdateStatus.ERROR)
                    logger.debug('Algun error en l\'ImportFile %s' % (urllib.parse.unquote_plus(impf.name)))
                else:
                    updateState(impf, UpdateStatus.FINISHED)
                    return True
            except Exception as e:
                updateState(impf, UpdateStatus.ERROR)
                msg = "An error ocurred importing %s: %s"
                logger.exception(msg, impf.name, str(e))
        return False

    @db_session
    def summary(self):
        try:
            alert_manager = AlertManager(**settings.MAIL)
            today = date.today()
            i_date = datetime(today.year, today.month, today.day, 0, 0, 0)
            f_date = i_date + timedelta(days=1)
            events = listEvents()
            impfs = listImportFiles_by_date_interval(i_date, f_date)
            errors = listCrawlingProcessErrors_by_date_interval(i_date, f_date)
            alert_manager.summary_send(
		self.date_events_task,
		i_date,
		f_date,
		events,
		impfs,
               errors
	    )
            alert_manager.close()
        except Exception as e:
            logger.error("Exception raised sending crawl summary: ", e)
        else:
            return True
