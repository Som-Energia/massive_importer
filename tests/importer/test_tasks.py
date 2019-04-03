import os, sys, json
from datetime import datetime
from unittest import TestCase
from pony.orm import db_session, sql_debug, count, select, set_sql_debug

os.environ.setdefault('MASSIVE_IMPORTER_SETTINGS', 'massive_importer.conf.envs.test')

from massive_importer.models.importer import Event, ImportFile, UpdateStatus, db
from massive_importer.conf.startup_configuration import build_app, settings
from tests.importer.testdb import populate_events_database, populate_impFile_database


class TaskTest(TestCase):
    
    @classmethod
    def setUpClass(cls):  
        db.bind(**settings.DATABASE)
        db.generate_mapping(create_tables=True)
        populate_events_database()
        # set_sql_debug(True)

    @db_session
    def test_listEvents(self):
        file1 = db.Event.get(key="proves/object.txt")
        file2 = db.Event.get(key="proves/asd.txt")
        file3 = db.Event.get(key="proves/diagrama.zip")

        self.assertEqual(file1.value['Records'][0]['s3']['object']['key'], "object.txt")
        self.assertEqual(file1.value['Records'][0]['s3']['object']['eTag'], "d41d8cd98f00b204e9800998ecf8427e")

        self.assertEqual(file2.value['Records'][0]['s3']['object']['key'], "asd.txt")
        self.assertEqual(file2.value['Records'][0]['s3']['object']['eTag'], "d41d8cd98f00b204e9800998ecf8427a")

        self.assertEqual(file3.value['Records'][0]['s3']['object']['key'], "diagrama.zip")
        self.assertEqual(file3.value['Records'][0]['s3']['object']['eTag'], "00251585078848321d4e3ed5c3e699a2")
        
    @db_session
    def test_eventToImportFile(self):

        events = select(event for event in Event)
        for event in events:     
            eventname = event.value['Records'][0]['s3']['object']['key']
            eventetag = event.value['Records'][0]['s3']['object']['eTag']
            eventsize = event.value['Records'][0]['s3']['object']['size']
            ImpFile = ImportFile(etag=eventetag, name=eventname, size=eventsize)
        
            if (ImpFile): # Actualitzem l'estat
                self.assertTrue(ImpFile.state == 'ready')
            else:
                self.fail("Error on create ImportFile db entry")

    @db_session
    def test_updateState(self):
        # populate_impFile_database()
        impfiles = list(select(impf for impf in ImportFile))
        
        impfile1  = impfiles[0]
        impfile1.set(state=UpdateStatus.IN_PROCESS, modified_at=datetime.now())
        modified1 = list(select(impf for impf in ImportFile if impf.state==UpdateStatus.IN_PROCESS))

        impfile2  = impfiles[1]
        impfile2.set(state=UpdateStatus.FINISHED, modified_at=datetime.now())
        modified2 = list(select(impf for impf in ImportFile if impf.state==UpdateStatus.FINISHED))

        self.assertEqual(modified1[0].etag, impfile1.etag)
        self.assertEqual(modified2[0].etag, impfile2.etag)
        
    @classmethod
    def tearDownClass(cls):
        db.drop_all_tables(with_all_data=True)
        db.disconnect()