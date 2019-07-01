import os
from massive_importer.lib.alert_utils import AlertManager
from datetime import datetime, date
from massive_importer.models.importer import Event, ImportFile, db
from pony.orm import db_session
from massive_importer.conf import settings
from massive_importer.lib.db_utils import listEvents, listImportFiles
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/')


db.bind(**settings.DATABASE)
db.generate_mapping(create_tables=True)

@db_session
def create_event_list():
    e1 = Event(key="zips/fit4.zip", value={'Records':[{'s3':{'bucket':{'arn':'arn:aws:s3:::test','name':'test','ownerIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'}},'object':{'key':'fit1.zip','eTag':'87b416894d0d12580610f3e26a1120b8','size':5804,'sequencer':'159855F93736EE7C','versionId':'1','contentType':'application/zip','userMetadata':{'content-type':'application/zip'}},'configurationId':'Config','s3SchemaVersion':'1.0'},'source':{'host':'','port':'','userAgent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/73.0.3683.86 Chrome/73.0.3683.86 Safari/537.36'},'awsRegion':'','eventName':'s3:ObjectCreated:Put','eventTime':'2019-04-24T06:43:20Z','eventSource':'minio:s3','eventVersion':'2.0','userIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'},'responseElements':{'x-amz-request-id':'159855F936ECEFB0','x-minio-deployment-id':'4290b1de-9747-4f20-8c5e-4f4d64f24416','x-minio-origin-endpoint':'http://192.168.35.9:9000'},'requestParameters':{'region':'','accessKey':'NJHXYRAAILTKUVSXWDP9','sourceIPAddress':'127.0.0.1'}}]})
    e2 = Event(key="zips/fit5.zip", value={'Records':[{'s3':{'bucket':{'arn':'arn:aws:s3:::test','name':'test','ownerIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'}},'object':{'key':'fit2.zip','eTag':'59165058c94c753c75c492774d2c3db2','size':4137,'sequencer':'159855F93776F6A2','versionId':'1','contentType':'application/zip','userMetadata':{'content-type':'application/zip'}},'configurationId':'Config','s3SchemaVersion':'1.0'},'source':{'host':'','port':'','userAgent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/73.0.3683.86 Chrome/73.0.3683.86 Safari/537.36'},'awsRegion':'','eventName':'s3:ObjectCreated:Put','eventTime':'2019-04-24T06:43:20Z','eventSource':'minio:s3','eventVersion':'2.0','userIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'},'responseElements':{'x-amz-request-id':'159855F93714C388','x-minio-deployment-id':'4290b1de-9747-4f20-8c5e-4f4d64f24416','x-minio-origin-endpoint':'http://192.168.35.9:9000'},'requestParameters':{'region':'','accessKey':'NJHXYRAAILTKUVSXWDP9','sourceIPAddress':'127.0.0.1'}}]})
    e3 = Event(key="zips/fit6.zip", value={'Records':[{'s3':{'bucket':{'arn':'arn:aws:s3:::test','name':'test','ownerIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'}},'object':{'key':'fit3.zip','eTag':'a75b9c253823c292d69651890c73618a','size':4691,'sequencer':'159855F937CF001D','versionId':'1','contentType':'application/zip','userMetadata':{'content-type':'application/zip'}},'configurationId':'Config','s3SchemaVersion':'1.0'},'source':{'host':'','port':'','userAgent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/73.0.3683.86 Chrome/73.0.3683.86 Safari/537.36'},'awsRegion':'','eventName':'s3:ObjectCreated:Put','eventTime':'2019-04-24T06:43:20Z','eventSource':'minio:s3','eventVersion':'2.0','userIdentity':{'principalId':'NJHXYRAAILTKUVSXWDP9'},'responseElements':{'x-amz-request-id':'159855F9378329C1','x-minio-deployment-id':'4290b1de-9747-4f20-8c5e-4f4d64f24416','x-minio-origin-endpoint':'http://192.168.35.9:9000'},'requestParameters':{'region':'','accessKey':'NJHXYRAAILTKUVSXWDP9','sourceIPAddress':'127.0.0.1'}}]})
    return list([e1,e2,e3])

@db_session
def create_importfile_list():
    imFile1 = ImportFile(etag="99b416894d0d12580610f3e26a1120b8", name="zips/fit1.zip", bucket="test", size="584", msg="")
    imFile2 = ImportFile(etag="99165058c94c753c75c492774d2c3db2", name="zips/fit2.zip", bucket="test", size="437", msg="")
    imFile3 = ImportFile(etag="995b9c253823c292d69651890c73618a", name="zips/fit3.zip", bucket="test", size="461", msg="")
    return list([imFile1,imFile2,imFile3])

def create_summary(no_dates=False):
    if no_dates: example_date = None
    else:
        today = date.today()
        example_date = datetime(today.year, today.month, today.day, 0, 0, 0) 
    
    download_list = {'portal1':True, 'portal2':True, 'portal3':False}
    summary = { 
        'date_events_task': example_date,
        'i_date': example_date,
        'f_date': example_date,
        'event_list': create_event_list(),
        'importfile_list': create_importfile_list(),
        'date_download_task': example_date,
        'downloaded_list': download_list,
    }
    
    return summary

@db_session
def clean_tables():
    eventList = listEvents() 
    impList = listImportFiles()
    if eventList: 
        for event in eventList: event.delete()
    if impList:
        for impf in impList: impf.delete()

def get_content():
    with open(os.path.join(DATA_DIR, 'prova.zip'), 'rb') as f:
        content = f.read()
        return content

def get_bad_content():
    with open(os.path.join(DATA_DIR, 'bad_content.pdf'), 'rb') as f:
        content = f.read()
        return content