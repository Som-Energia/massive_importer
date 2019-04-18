# -*- coding: utf-8 -*-
import logging
import os
from unittest import TestCase
from datetime import datetime

from massive_importer.lib.minio_utils import MinioManager
from massive_importer.lib.erp_utils import ErpManager
from massive_importer.models.importer import db
from massive_importer.lib import db_utils
# from tests.lib.test_db import TestDbUtils

os.environ.setdefault('MASSIVE_IMPORTER_SETTINGS', 'massive_importer.conf.envs.test')

from massive_importer.conf import configure_logging, settings
from massive_importer.models.importer import Event, ImportFile, UpdateStatus
from pony.orm import select, db_session, delete
import time


logger = logging.getLogger(__name__)

class TaskTest(TestCase):

    @classmethod
    def setUpClass(cls): 
        db.bind(**settings.DATABASE)
        db.generate_mapping(create_tables=True)

        cls.minio_manager = MinioManager(**settings.MINIO)
        cls.erp_manager = ErpManager(**settings.ERP)
        cls.populate_events_database()
   
    @db_session
    def populate_events_database():
        e1 = Event(key="proves/object.txt", value={'Records':[{'s3':{'bucket':{'arn':'arn:aws:s3:::proves','name':'proves','ownerIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'}},'object':{'key':'object.txt','eTag':'d41d8cd98f00b204e9800998ecf8427e','size':17,'sequencer':'158F7C5867956E94','versionId':'1','contentType':'text/plain','userMetadata':{'content-type':'text/plain'}},'configurationId':'Config','s3SchemaVersion':'1.0'},'source':{'host':'','port':'','userAgent':'Minio (Linux; x86_64) minio-py/3.0.1'},'awsRegion':'','eventName':'s3:ObjectAccessed:Get','eventTime':'2019-03-26T10:45:15Z','eventSource':'minio:s3','eventVersion':'2.0','userIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'},'responseElements':{'content-length':'17','x-amz-request-id':'158F7C586788D4AA','x-minio-deployment-id':'4290b1de-9747-4f20-8c5e-4f4d64f24416','x-minio-origin-endpoint':'http://192.168.35.9:9000'},'requestParameters':{'region':'','accessKey':'NJHXYRAAILTKUVSXWDP9','sourceIPAddress':'127.0.0.1'}}]})
        e2 = Event(key="proves/asd.txt", value={'Records':[{'s3':{'bucket':{'arn':'arn:aws:s3:::proves','name':'proves','ownerIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'}},'object':{'key':'asd.txt','eTag':'d41d8cd98f00b204e9800998ecf8427a','size':6,'sequencer':'158F7C5867C6BBB5','versionId':'1','contentType':'text/plain','userMetadata':{'content-type':'text/plain'}},'configurationId':'Config','s3SchemaVersion':'1.0'},'source':{'host':'','port':'','userAgent':'Minio (Linux; x86_64) minio-py/3.0.1'},'awsRegion':'','eventName':'s3:ObjectAccessed:Get','eventTime':'2019-03-26T10:45:15Z','eventSource':'minio:s3','eventVersion':'2.0','userIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'},'responseElements':{'content-length':'6','x-amz-request-id':'158F7C5867C2C12E','x-minio-deployment-id':'4290b1de-9747-4f20-8c5e-4f4d64f24416','x-minio-origin-endpoint':'http://192.168.35.9:9000'},'requestParameters':{'region':'','accessKey':'NJHXYRAAILTKUVSXWDP9','sourceIPAddress':'127.0.0.1'}}]})
        e3 = Event(key="proves/diagrama.zip", value={'Records':[{'s3':{'bucket':{'arn':'arn:aws:s3:::proves','name':'proves','ownerIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'}},'object':{'key':'diagrama.zip','eTag':'00251585078848321d4e3ed5c3e699a2','size':2084,'sequencer':'15905ED1D42AA022','versionId':'1','contentType':'application/zip','userMetadata':{'content-type':'application/zip'}},'configurationId':'Config','s3SchemaVersion':'1.0'},'source':{'host':'','port':'','userAgent':'Minio (linux; amd64) minio-go/v6.0.20 mc/2019-03-13T21:05:06Z'},'awsRegion':'','eventName':'s3:ObjectCreated:Put','eventTime':'2019-03-29T07:55:26Z','eventSource':'minio:s3','eventVersion':'2.0','userIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'},'responseElements':{'x-amz-request-id':'15905ED1D3EF3BD9','x-minio-deployment-id':'4290b1de-9747-4f20-8c5e-4f4d64f24416','x-minio-origin-endpoint':'http://192.168.35.9:9000'},'requestParameters':{'region':'','accessKey':'NJHXYRAAILTKUVSXWDP9','sourceIPAddress':'127.0.0.1'}}]})

    def get_importFile_list(self):
        impfiles = db_utils.listImportFiles()
        self.assertIsNotNone(impfiles)
        return impfiles

    def get_event_list(self):
        events = db_utils.listEvents()
        self.assertIsNotNone(events)
        return events
    
    @db_session
    def test_check_new_events(self):
        events = self.get_event_list()
        for event in events:
            impf = None
            eventname = event.value['Records'][0]['s3']['object']['key']
            eventetag = event.value['Records'][0]['s3']['object']['eTag']
            bucketname = event.value['Records'][0]['s3']['bucket']['name']
            eventsize = event.value['Records'][0]['s3']['object']['size']
            impf = ImportFile(etag=eventetag, name=eventname, bucket=bucketname, size=eventsize)
            self.assertIsNotNone(impf)
            event.delete()
        self.assertFalse(len(self.get_event_list()))

    @db_session
    def test_import_zips(self):
        impfs = self.get_importFile_list()
        for impf in impfs:
            impf.set(state=UpdateStatus.IN_PROCESS, modified_at=datetime.now())
            self.assertEqual(impf.state, UpdateStatus.IN_PROCESS)

            # TODO: El test que ha de passar és el de test_erpmanager.py

            impf.set(state=UpdateStatus.FINISHED, modified_at=datetime.now())
            self.assertEqual(impf.state, UpdateStatus.FINISHED)
   
    @classmethod
    def tearDownClass(cls):
        db.drop_all_tables(with_all_data=True)
        db.disconnect()
        