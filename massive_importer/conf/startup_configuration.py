# -*- coding: utf-8 -*-
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from pony.orm import Database

from massive_importer.conf import configure_logging, settings
from massive_importer.models.importer import db
from massive_importer.importer.tasks import import_zips

logger = logging.getLogger('massive_importer.conf')


def build_app():
    try:
        configure_logging(settings.LOGGING)

        db.bind(**settings.DATABASE)
        db.generate_mapping(create_tables=True)

        scheduler = BlockingScheduler(
            executors=settings.EXECUTORS
        )

    except Exception as e:
        msg = "An error ocurred building massive_importer: %s"
        logger.exception(msg, e)
        raise e

    logger.debug("Build app finished")
    return scheduler


def add_jobs(app):
    logger.debug("Adding task: %s", import_zips.__name__)
    app.add_job(import_zips, **settings.TASKS[import_zips.__name__])
