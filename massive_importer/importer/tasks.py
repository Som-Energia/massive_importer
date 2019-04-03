# -*- coding: utf-8 -*-
import logging
import time
import os
from datetime import datetime

from massive_importer.lib.minio_utils import MinioManager
from massive_importer.conf import configure_logging, settings
from massive_importer.models.importer import Event, ImportFile, UpdateStatus

from pony.orm import select, db_session, delete


logger = logging.getLogger(__name__)
minio_manager = MinioManager(**settings.MINIO)

@db_session
def listEvents():
    ret = select(event for event in Event)
    return list(ret)

@db_session
def eventToImportFile(event):    
    eventname = event.value['Records'][0]['s3']['object']['key']
    eventetag = event.value['Records'][0]['s3']['object']['eTag']
    eventsize = event.value['Records'][0]['s3']['object']['size']
    return ImportFile(etag=eventetag, name=eventname, size=eventsize)

@db_session
def updateState(impf, state):
    impf.set(state=state, modified_at=date.now())

@db_session
def import_zips():
    logger.debug("Importando zips!")
    eventList = listEvents()
    if eventList:
        for event in eventList:
            ImpFile = eventToImportFile(event)
            updateState(ImpFile, UpdateStatus.IN_PROCESS)
            event.delete()
            tmpFile = None
            try:
                bucket = event.value['Records'][0]['s3']['bucket']['name']
                file_name = event.value['Records'][0]['s3']['object']['key']
                tmpFile = minio_manager.get_file_content(bucket, file_name)
            except:
                updateState(ImpFile, UpdateStatus.ERROR)
                print("Error getting file content from Minio bucket")
            
            if tmpFile:   
                # He de carregar el fitxer al ERP, a través del wizard
                
                updateState(ImpFile, UpdateStatus.FINISHED)            

    else: logger.debug("No events found")        

    logger.debug("Ya he terminado :)")
