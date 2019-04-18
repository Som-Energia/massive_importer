from massive_importer.models.importer import Event, ImportFile, UpdateStatus
from pony.orm import select, db_session, delete
from datetime import datetime

@db_session
def listImportFiles():
    ret = select(impf for impf in ImportFile)
    return list(ret)

@db_session
def listEvents():
    ret = select(event for event in Event)
    return list(ret)

@db_session
def eventToImportFile(event):    
    eventname = event.value['Records'][0]['s3']['object']['key']
    eventetag = event.value['Records'][0]['s3']['object']['eTag']
    bucketname = event.value['Records'][0]['s3']['bucket']['name']
    try:
        eventsize = event.value['Records'][0]['s3']['object']['size']
    except:
        print("Error: Event <<",eventname ,">> reffers to an empty file.")
    return ImportFile(etag=eventetag, name=eventname, bucket=bucketname, size=eventsize)

@db_session
def updateState(impf, state):
    impf.set(state=state, modified_at=datetime.now())