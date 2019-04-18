# -*- coding: utf-8 -*-
import logging

from massive_importer.lib.minio_utils import MinioManager
from massive_importer.lib.erp_utils import ErpManager
from massive_importer.lib.db_utils import listEvents, updateState, eventToImportFile
from massive_importer.conf import configure_logging, settings
from massive_importer.models.importer import Event, ImportFile, UpdateStatus
from pony.orm import select, db_session, delete
from multiprocessing import Process
import time

logger = logging.getLogger(__name__)
minio_manager = MinioManager(**settings.MINIO)
erp_manager = ErpManager(**settings.ERP)

@db_session(optimistic=False)
def check_new_events():
    if erp_manager== None :
        raise ValueError("There is no ERP Connection")

    logger.debug("***Importando zips!***")
    eventList = listEvents()
    if eventList:
        for event in eventList:
            impf = eventToImportFile(event)
            if(impf):
                event.delete()
                import_zips(impf)

                
    else: logger.debug("No events found")        

    logger.debug("***Ya he terminado :)***")


def import_zips(impf):
    updateState(impf, UpdateStatus.IN_PROCESS)
    content = None
    try:
        content = minio_manager.get_file_content(impf.bucket, impf.name)
    except:
        updateState(impf, UpdateStatus.ERROR)
        print("Error getting file content from Minio bucket")
    else:
        try: 
            erp_manager.import_wizard(impf.name, content)
            updateState(impf, UpdateStatus.FINISHED)
        except Exception as e:
            msg = "An error ocurred importing %s: %s"
            logger.exception(msg, impf.name, str(e))
