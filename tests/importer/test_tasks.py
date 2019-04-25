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
import concurrent.futures


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
        e1 = Event(key="proves/fit1.zip", value={'Records':[{'s3':{'bucket':{'arn':'arn:aws:s3:::proves','name':'proves','ownerIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'}},'object':{'key':'fit1.zip','eTag':'87b416894d0d12580610f3e26a1120b8','size':5804,'sequencer':'159855F93736EE7C','versionId':'1','contentType':'application/zip','userMetadata':{'content-type':'application/zip'}},'configurationId':'Config','s3SchemaVersion':'1.0'},'source':{'host':'','port':'','userAgent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/73.0.3683.86 Chrome/73.0.3683.86 Safari/537.36'},'awsRegion':'','eventName':'s3:ObjectCreated:Put','eventTime':'2019-04-24T06:43:20Z','eventSource':'minio:s3','eventVersion':'2.0','userIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'},'responseElements':{'x-amz-request-id':'159855F936ECEFB0','x-minio-deployment-id':'4290b1de-9747-4f20-8c5e-4f4d64f24416','x-minio-origin-endpoint':'http://192.168.35.9:9000'},'requestParameters':{'region':'','accessKey':'NJHXYRAAILTKUVSXWDP9','sourceIPAddress':'127.0.0.1'}}]})
        e2 = Event(key="proves/fit2.zip", value={'Records':[{'s3':{'bucket':{'arn':'arn:aws:s3:::proves','name':'proves','ownerIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'}},'object':{'key':'fit2.zip','eTag':'59165058c94c753c75c492774d2c3db2','size':4137,'sequencer':'159855F93776F6A2','versionId':'1','contentType':'application/zip','userMetadata':{'content-type':'application/zip'}},'configurationId':'Config','s3SchemaVersion':'1.0'},'source':{'host':'','port':'','userAgent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/73.0.3683.86 Chrome/73.0.3683.86 Safari/537.36'},'awsRegion':'','eventName':'s3:ObjectCreated:Put','eventTime':'2019-04-24T06:43:20Z','eventSource':'minio:s3','eventVersion':'2.0','userIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'},'responseElements':{'x-amz-request-id':'159855F93714C388','x-minio-deployment-id':'4290b1de-9747-4f20-8c5e-4f4d64f24416','x-minio-origin-endpoint':'http://192.168.35.9:9000'},'requestParameters':{'region':'','accessKey':'NJHXYRAAILTKUVSXWDP9','sourceIPAddress':'127.0.0.1'}}]})
        e3 = Event(key="proves/fit3.zip", value={'Records':[{'s3':{'bucket':{'arn':'arn:aws:s3:::proves','name':'proves','ownerIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'}},'object':{'key':'fit3.zip','eTag':'a75b9c253823c292d69651890c73618a','size':4691,'sequencer':'159855F937CF001D','versionId':'1','contentType':'application/zip','userMetadata':{'content-type':'application/zip'}},'configurationId':'Config','s3SchemaVersion':'1.0'},'source':{'host':'','port':'','userAgent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/73.0.3683.86 Chrome/73.0.3683.86 Safari/537.36'},'awsRegion':'','eventName':'s3:ObjectCreated:Put','eventTime':'2019-04-24T06:43:20Z','eventSource':'minio:s3','eventVersion':'2.0','userIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'},'responseElements':{'x-amz-request-id':'159855F9378329C1','x-minio-deployment-id':'4290b1de-9747-4f20-8c5e-4f4d64f24416','x-minio-origin-endpoint':'http://192.168.35.9:9000'},'requestParameters':{'region':'','accessKey':'NJHXYRAAILTKUVSXWDP9','sourceIPAddress':'127.0.0.1'}}]})

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
        impfs = []
        for event in events:
            eventname = event.value['Records'][0]['s3']['object']['key']
            eventetag = event.value['Records'][0]['s3']['object']['eTag']
            bucketname = event.value['Records'][0]['s3']['bucket']['name']
            eventsize = event.value['Records'][0]['s3']['object']['size']
            impf = ImportFile(etag=eventetag, name=eventname, bucket=bucketname, size=eventsize)
            self.assertIsNotNone(impf)
            impfs.append(impf) 
            event.delete()
        self.assertFalse(len(self.get_event_list()))
        
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

        # TODO: El test que ha de passar és el de test_erpmanager.py
        # print('File %s uploaded.' % (impf.name))

        impf.set(state=UpdateStatus.FINISHED, modified_at=datetime.now())
        self.assertEqual(impf.state, UpdateStatus.FINISHED)
        return True
      
    @classmethod
    def tearDownClass(cls):
        db.drop_all_tables(with_all_data=True)
        db.disconnect()
        