# -*- coding: utf-8 -*-
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from pony.orm import Database

from massive_importer.conf import configure_logging, settings
from massive_importer.models.importer import db
from massive_importer.importer.tasks import check_new_events, web_crawling

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
    logger.debug("Adding task: %s", check_new_events.__name__)
    app.add_job(check_new_events, **settings.TASKS[check_new_events.__name__])
    logger.debug("Adding task: %s", web_crawling.__name__)
    app.add_job(web_crawling, **settings.TASKS[web_crawling.__name__])
