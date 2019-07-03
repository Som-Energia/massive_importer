from unittest import TestCase
import concurrent.futures
from multiprocessing import Process
import logging, time, urllib, threading, datetime, os
from datetime import datetime, date, timedelta
from massive_importer.crawlers.run_crawlers import MockWebCrawler
from massive_importer.lib.minio_utils import MinioManager
from massive_importer.lib.erp_utils import MockErpManager
from massive_importer.lib.db_utils import listEvents, listImportFiles, listImportFiles_by_date_interval, updateState, eventToImportFile
from massive_importer.lib.alert_utils import AlertManager

os.environ.setdefault('MASSIVE_IMPORTER_SETTINGS', 'massive_importer.conf.envs.test')

from massive_importer.conf import configure_logging, settings
from massive_importer.models.importer import Event, ImportFile, UpdateStatus, db
from pony.orm import select, db_session, delete
import concurrent.futures
from multiprocessing import Process


logger = logging.getLogger(__name__)

MAX_NUM_RETRIES = 3

class TestTasks(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.minio_manager = MinioManager(**settings.MINIO, default_bucket="zips")
        cls.erp_manager = MockErpManager()
        db.bind(**settings.DATABASE)
        db.generate_mapping(create_tables=True)
        cls.clean()
        files = ['fit1.zip','fit2.zip','fit3.zip','fit4.zip']
        for item in files:   
            with open(os.path.join(os.path.dirname(os.path.dirname(__file__)),'data/', item), 'rb') as content:
                data = content.read()
                cls.minio_manager.put_file(cls.minio_manager.default_bucket, item, data)
    
    @classmethod
    def clean(self):
        self.minio_manager.full_clean('zips')
        for event in listEvents():
            event.delete()
        for impf in listImportFiles():
            impf.delete()

    def test_web_crawling(self):
        wc = MockWebCrawler().crawl()
        files = self.minio_manager.list_objects(self.minio_manager.default_bucket)
        self.assertTrue(files != None)

    @db_session
    def test_check_new_events(self):
        impfs = []
        eventList = listEvents()
        self.assertIsNotNone(eventList)
        logger.error(eventList)

        if eventList:          
            for event in eventList: 
                impf = eventToImportFile(event) 
                if impf: 
                    impfs.append(impf) 
                    event.delete()
        self.assertFalse(len(listEvents())) 
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor: 
            future_to_events = {executor.submit(self._import_zips, impf): impf for impf in impfs} 
            for future in concurrent.futures.as_completed(future_to_events): 
                event = future_to_events[future] 
                try: 
                    res = future.result() 
                except Exception as exc: 
                    self.fail('generated an exception:', exc)
                else: 
                    self.assertTrue(res) 

    @db_session
    def _import_zips(self, impf):
        impf.set(state=UpdateStatus.IN_PROCESS, modified_at=datetime.now())
        self.assertEqual(impf.state, UpdateStatus.IN_PROCESS)
        impf.set(state=UpdateStatus.FINISHED, modified_at=datetime.now())
        self.assertEqual(impf.state, UpdateStatus.FINISHED)
        return True
        
    @db_session
    def test_summary(self):
        alert_manager = AlertManager(**settings.MAIL)
        today = date.today()
        i_date = datetime(today.year, today.month, today.day, 0, 0, 0)
        f_date = i_date + timedelta(days=1)
        events = listEvents()
        impfs = listImportFiles_by_date_interval(i_date, f_date)
        alert_manager.summary_send(i_date, f_date, events, impfs)

    @classmethod
    @db_session
    def tearDownClass(cls):
        cls.clean()
