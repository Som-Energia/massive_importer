from massive_importer.models.importer import Event, ImportFile, UpdateStatus, CrawlingProcessError
from pony.orm import select, db_session, delete
from datetime import datetime
import logging
from massive_importer.lib.exceptions import EventToImportFileException

logger = logging.getLogger(__name__)

@db_session
def listImportFiles():
    ret = select(impf for impf in ImportFile)
    return list(ret)

@db_session
def listImportFiles_by_date_interval(i_date, f_date):
    ret = select(impf for impf in ImportFile if (impf.created_at >= i_date and impf.created_at < f_date))
    return list(ret)

@db_session
def listCrawlingProcessErrors_by_date_interval(i_date, f_date):
    ret = select(error for error in CrawlingProcessError if (error.created_at >= i_date and error.created_at < f_date))
    return list(ret)

@db_session
def listEvents():
    ret = select(event for event in Event)
    return list(ret)

@db_session
def eventToImportFile(event):
    impf = None
    eventname = event.value['Records'][0]['s3']['object']['key']
    eventetag = event.value['Records'][0]['s3']['object']['eTag']
    bucketname = event.value['Records'][0]['s3']['bucket']['name']
    eventsize = event.value['Records'][0]['s3']['object']['size']
    eventportal = event.value['Records'][0]['s3']['object']['userMetadata']['X-Amz-Meta-Portal']
    try:
        impf = ImportFile(etag=eventetag, name=eventname, bucket=bucketname, size=eventsize, portal=eventportal)
        return impf
    except Exception as e:
        raise EventToImportFileException(e)
    else:
        return impf

@db_session
def updateState(impf, state):
    impf.set(state=state, modified_at=datetime.now())

@db_session
def checkEtag(event):
    eventetag = event.value['Records'][0]['s3']['object']['eTag']
    impf = ImportFile.get(etag=eventetag)
    return True if impf else False

@db_session
def delete_events(eventList):
    if eventList:
        for event in eventList:
            event.delete()

@db_session
def insert_crawling_process_error(crawler_name, e):
    CrawlingProcessError(
        crawler_name=crawler_name,
        exception_type=str(e.__class__),
        description=str(e)
    )
