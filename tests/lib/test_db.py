import os, sys, json, logging
from datetime import datetime, date,timedelta
from unittest import TestCase
from pony.orm import db_session, sql_debug, count, select, set_sql_debug

os.environ.setdefault('MASSIVE_IMPORTER_SETTINGS', 'massive_importer.conf.envs.test')
from massive_importer.models.importer import UpdateStatus, db
from massive_importer.conf import settings
from massive_importer.lib import db_utils

from .testhelper import TestHelper
testhelper = TestHelper()
logger = logging.getLogger(__name__)


class TestDbUtils(TestCase):
    
    @classmethod
    def setUpClass(cls): 
        testhelper.create_event_list()
        testhelper.create_importfile_list()

    def test_listImportFiles(self):
        impfs = db_utils.listImportFiles()
        self.assertTrue(len(impfs)>0)

    def test_listImportFiles_by_date_interval(self):
        today = date.today()
        i_date = datetime(today.year, today.month, today.day, 0, 0, 0)
        f_date = i_date + timedelta(days=1)
        impfs = db_utils.listImportFiles_by_date_interval(i_date, f_date)
        self.assertTrue(len(impfs)>0)

        i_date_new = i_date - timedelta(days=10)
        f_date_new = f_date - timedelta(days=10)
        impfs_new = db_utils.listImportFiles_by_date_interval(i_date_new, f_date_new)
        self.assertFalse(len(impfs_new))

    def test_listEvents(self):
        events = db_utils.listEvents()
        self.assertTrue(len(events)>0)

    def test_eventToImportFile(self):
        impfs_i = db_utils.listImportFiles()
        events = db_utils.listEvents()
        for event in events:
            db_utils.eventToImportFile(event)
        impfs_f = db_utils.listImportFiles()
        self.assertTrue(len(impfs_f) > len(impfs_i))

    @db_session
    def test_updateState(self):
        impfs = db_utils.listImportFiles()
        for impf in impfs:
            db_utils.updateState(impf, UpdateStatus.FINISHED)
        impfs_after = db_utils.listImportFiles()
        for impf in impfs_after:
            self.assertEqual(impf.state, 'ok')

    @classmethod
    def tearDownClass(cls):
        # db.drop_all_tables(with_all_data=True)
        testhelper.clean_tables()
        testhelper.disconnect_db()
