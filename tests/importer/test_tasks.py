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
from massive_importer.importer.tasks import Tasks

logger = logging.getLogger(__name__)
from tests.lib import test_helper


class TestTasks(TestCase):
    @classmethod
    def setUpClass(cls):
        test_helper.clean_tables()
        cls.tasks = Tasks(erp_manager=MockErpManager(), web_crawler=MockWebCrawler())

    def tearDown(self):
        self.tasks.minio_manager.full_clean(self.tasks.minio_manager.default_bucket)

    def test_web_crawling(self):
        self.tasks.web_crawling()
        for item in self.tasks.downloaded_list:
            self.assertEqual(item, 'testSpider' )
            self.assertEqual(self.tasks.downloaded_list[item], True)

    def test_check_new_events(self):
        if not self.tasks.downloaded_list: 
            self.tasks.web_crawling()
        self.tasks.check_new_events()
        self.assertIsNotNone(self.tasks.date_events_task)

    @db_session
    def test_import_zips(self):
        test_helper.create_importfile_list()
        for item in listImportFiles():
            ret = self.tasks.import_zips(item)
            self.assertTrue(ret)

    def test_summary(self):
        today = date.today()
        self.tasks.date_events_task = datetime(today.year, today.month, today.day, 0, 0, 0)  
        self.tasks.date_download_task = datetime(today.year, today.month, today.day, 0, 0, 0) 
        if not self.tasks.downloaded_list:
            self.tasks.downloaded_list = {'testSpider'}
        ret = self.tasks.summary()
        self.assertTrue(ret)
        
    @classmethod
    def tearDownClass(cls):
        test_helper.clean_tables()
