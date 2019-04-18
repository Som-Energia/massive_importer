import os, sys, json
from datetime import datetime
from unittest import TestCase
from pony.orm import db_session, sql_debug, count, select, set_sql_debug

os.environ.setdefault('MASSIVE_IMPORTER_SETTINGS', 'massive_importer.conf.envs.test')

from massive_importer.models.importer import Event, ImportFile, UpdateStatus, db
from massive_importer.conf.startup_configuration import settings

class TestDbUtils(TestCase):
    
    @classmethod
    def setUpClass(cls):  
        db.bind(**settings.DATABASE)
        db.generate_mapping(create_tables=True)
        cls.populate_events_database()
        set_sql_debug(True)

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
        e1 = Event(key="proves/object.txt", value={'Records':[{'s3':{'bucket':{'arn':'arn:aws:s3:::proves','name':'proves','ownerIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'}},'object':{'key':'object.txt','eTag':'d41d8cd98f00b204e9800998ecf8427e','size':17,'sequencer':'158F7C5867956E94','versionId':'1','contentType':'text/plain','userMetadata':{'content-type':'text/plain'}},'configurationId':'Config','s3SchemaVersion':'1.0'},'source':{'host':'','port':'','userAgent':'Minio (Linux; x86_64) minio-py/3.0.1'},'awsRegion':'','eventName':'s3:ObjectAccessed:Get','eventTime':'2019-03-26T10:45:15Z','eventSource':'minio:s3','eventVersion':'2.0','userIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'},'responseElements':{'content-length':'17','x-amz-request-id':'158F7C586788D4AA','x-minio-deployment-id':'4290b1de-9747-4f20-8c5e-4f4d64f24416','x-minio-origin-endpoint':'http://192.168.35.9:9000'},'requestParameters':{'region':'','accessKey':'NJHXYRAAILTKUVSXWDP9','sourceIPAddress':'127.0.0.1'}}]})
        e2 = Event(key="proves/asd.txt", value={'Records':[{'s3':{'bucket':{'arn':'arn:aws:s3:::proves','name':'proves','ownerIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'}},'object':{'key':'asd.txt','eTag':'d41d8cd98f00b204e9800998ecf8427a','size':6,'sequencer':'158F7C5867C6BBB5','versionId':'1','contentType':'text/plain','userMetadata':{'content-type':'text/plain'}},'configurationId':'Config','s3SchemaVersion':'1.0'},'source':{'host':'','port':'','userAgent':'Minio (Linux; x86_64) minio-py/3.0.1'},'awsRegion':'','eventName':'s3:ObjectAccessed:Get','eventTime':'2019-03-26T10:45:15Z','eventSource':'minio:s3','eventVersion':'2.0','userIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'},'responseElements':{'content-length':'6','x-amz-request-id':'158F7C5867C2C12E','x-minio-deployment-id':'4290b1de-9747-4f20-8c5e-4f4d64f24416','x-minio-origin-endpoint':'http://192.168.35.9:9000'},'requestParameters':{'region':'','accessKey':'NJHXYRAAILTKUVSXWDP9','sourceIPAddress':'127.0.0.1'}}]})
        e3 = Event(key="proves/diagrama.zip", value={'Records':[{'s3':{'bucket':{'arn':'arn:aws:s3:::proves','name':'proves','ownerIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'}},'object':{'key':'diagrama.zip','eTag':'00251585078848321d4e3ed5c3e699a2','size':2084,'sequencer':'15905ED1D42AA022','versionId':'1','contentType':'application/zip','userMetadata':{'content-type':'application/zip'}},'configurationId':'Config','s3SchemaVersion':'1.0'},'source':{'host':'','port':'','userAgent':'Minio (linux; amd64) minio-go/v6.0.20 mc/2019-03-13T21:05:06Z'},'awsRegion':'','eventName':'s3:ObjectCreated:Put','eventTime':'2019-03-29T07:55:26Z','eventSource':'minio:s3','eventVersion':'2.0','userIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'},'responseElements':{'x-amz-request-id':'15905ED1D3EF3BD9','x-minio-deployment-id':'4290b1de-9747-4f20-8c5e-4f4d64f24416','x-minio-origin-endpoint':'http://192.168.35.9:9000'},'requestParameters':{'region':'','accessKey':'NJHXYRAAILTKUVSXWDP9','sourceIPAddress':'127.0.0.1'}}]})

    @db_session
    def populate_impFile_database():
        imFile1 = ImportFile(etag="d41d8cd98f00b204e9800998ecf8427e", name="object.txt", bucket="proves", size="17", msg="")
        imFile2 = ImportFile(etag="d41d8cd98f00b204e9800998ecf8427a", name="asd.txt", bucket="proves", size="6", msg="")
        imFile3 = ImportFile(etag="00251585078848321d4e3ed5c3e699a2", name="diagrama.zip", bucket="proves", size="2084", msg="")
    
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