import os, sys, json
from datetime import datetime
from unittest import TestCase
from pony.orm import db_session, sql_debug, count, select, set_sql_debug

os.environ.setdefault('MASSIVE_IMPORTER_SETTINGS', 'massive_importer.conf.envs.test')

from massive_importer.models.importer import Event, ImportFile, UpdateStatus, db
from massive_importer.conf import settings

class TestDbUtils(TestCase):
    
    @classmethod
    def setUpClass(cls):  
        db.bind(**settings.DATABASE)
        db.generate_mapping(create_tables=True)
        cls.populate_events_database()

    @db_session
    def test_listEvents(self):
        file1 = db.Event.get(key="zips/fit1.zip")
        file2 = db.Event.get(key="zips/fit2.zip")
        file3 = db.Event.get(key="zips/fit3.zip")

        self.assertEqual(file1.value['Records'][0]['s3']['object']['key'], "fit1.zip")
        self.assertEqual(file1.value['Records'][0]['s3']['object']['eTag'], "87b416894d0d12580610f3e26a1120b8")

        self.assertEqual(file2.value['Records'][0]['s3']['object']['key'], "fit2.zip")
        self.assertEqual(file2.value['Records'][0]['s3']['object']['eTag'], "59165058c94c753c75c492774d2c3db2")

        self.assertEqual(file3.value['Records'][0]['s3']['object']['key'], "fit3.zip")
        self.assertEqual(file3.value['Records'][0]['s3']['object']['eTag'], "a75b9c253823c292d69651890c73618a")

    @db_session
    def test_eventToImportFile(self):

        events = select(event for event in Event)
        for event in events:     
            eventname = event.value['Records'][0]['s3']['object']['key']
            eventetag = event.value['Records'][0]['s3']['object']['eTag']
            eventsize = event.value['Records'][0]['s3']['object']['size']
            bucketname = event.value['Records'][0]['s3']['bucket']['name']
            ImpFile = ImportFile(etag=eventetag, name=eventname, bucket=bucketname, size=eventsize)
        
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

    @db_session
    def populate_events_database():
        e1 = Event(key="zips/fit1.zip", value={'Records':[{'s3':{'bucket':{'arn':'arn:aws:s3:::test','name':'test','ownerIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'}},'object':{'key':'fit1.zip','eTag':'87b416894d0d12580610f3e26a1120b8','size':5804,'sequencer':'159855F93736EE7C','versionId':'1','contentType':'application/zip','userMetadata':{'content-type':'application/zip'}},'configurationId':'Config','s3SchemaVersion':'1.0'},'source':{'host':'','port':'','userAgent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/73.0.3683.86 Chrome/73.0.3683.86 Safari/537.36'},'awsRegion':'','eventName':'s3:ObjectCreated:Put','eventTime':'2019-04-24T06:43:20Z','eventSource':'minio:s3','eventVersion':'2.0','userIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'},'responseElements':{'x-amz-request-id':'159855F936ECEFB0','x-minio-deployment-id':'4290b1de-9747-4f20-8c5e-4f4d64f24416','x-minio-origin-endpoint':'http://192.168.35.9:9000'},'requestParameters':{'region':'','accessKey':'NJHXYRAAILTKUVSXWDP9','sourceIPAddress':'127.0.0.1'}}]})
        e2 = Event(key="zips/fit2.zip", value={'Records':[{'s3':{'bucket':{'arn':'arn:aws:s3:::test','name':'test','ownerIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'}},'object':{'key':'fit2.zip','eTag':'59165058c94c753c75c492774d2c3db2','size':4137,'sequencer':'159855F93776F6A2','versionId':'1','contentType':'application/zip','userMetadata':{'content-type':'application/zip'}},'configurationId':'Config','s3SchemaVersion':'1.0'},'source':{'host':'','port':'','userAgent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/73.0.3683.86 Chrome/73.0.3683.86 Safari/537.36'},'awsRegion':'','eventName':'s3:ObjectCreated:Put','eventTime':'2019-04-24T06:43:20Z','eventSource':'minio:s3','eventVersion':'2.0','userIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'},'responseElements':{'x-amz-request-id':'159855F93714C388','x-minio-deployment-id':'4290b1de-9747-4f20-8c5e-4f4d64f24416','x-minio-origin-endpoint':'http://192.168.35.9:9000'},'requestParameters':{'region':'','accessKey':'NJHXYRAAILTKUVSXWDP9','sourceIPAddress':'127.0.0.1'}}]})
        e3 = Event(key="zips/fit3.zip", value={'Records':[{'s3':{'bucket':{'arn':'arn:aws:s3:::test','name':'test','ownerIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'}},'object':{'key':'fit3.zip','eTag':'a75b9c253823c292d69651890c73618a','size':4691,'sequencer':'159855F937CF001D','versionId':'1','contentType':'application/zip','userMetadata':{'content-type':'application/zip'}},'configurationId':'Config','s3SchemaVersion':'1.0'},'source':{'host':'','port':'','userAgent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/73.0.3683.86 Chrome/73.0.3683.86 Safari/537.36'},'awsRegion':'','eventName':'s3:ObjectCreated:Put','eventTime':'2019-04-24T06:43:20Z','eventSource':'minio:s3','eventVersion':'2.0','userIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'},'responseElements':{'x-amz-request-id':'159855F9378329C1','x-minio-deployment-id':'4290b1de-9747-4f20-8c5e-4f4d64f24416','x-minio-origin-endpoint':'http://192.168.35.9:9000'},'requestParameters':{'region':'','accessKey':'NJHXYRAAILTKUVSXWDP9','sourceIPAddress':'127.0.0.1'}}]})

    @db_session
    def populate_impFile_database():
        imFile1 = ImportFile(etag="87b416894d0d12580610f3e26a1120b8", name="zips/fit1.zip", bucket="test", size="5804", msg="")
        imFile2 = ImportFile(etag="59165058c94c753c75c492774d2c3db2", name="zips/fit2.zip", bucket="test", size="4137", msg="")
        imFile3 = ImportFile(etag="a75b9c253823c292d69651890c73618a", name="zips/fit3.zip", bucket="test", size="4691", msg="")
    
    @db_session
    def list_queries():
        print('\n*All Events*') 
        ret = select(event for event in Event)
        for event in list(ret):
            print(event.key)

        print('\n*All Import_files*')
        namewidth = 25
        ret = select(impfile for impfile in ImportFile)
        for impfile in list(ret):
            print(impfile.id, " ", impfile.name," "*(namewidth-len(impfile.name)),impfile.state," ",impfile.created_at)

    @classmethod
    def tearDownClass(cls):
        db.drop_all_tables(with_all_data=True)
        db.disconnect()