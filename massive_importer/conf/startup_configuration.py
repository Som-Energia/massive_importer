# -*- coding: utf-8 -*-
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from pony.orm import Database

from massive_importer.conf import configure_logging, settings
from massive_importer.models.importer import db
from massive_importer.importer.tasks import Tasks

logger = logging.getLogger('massive_importer.conf')


def build_app(args):
    try:
        if args.debug:
            settings.DEBUG_MODE = True
        configure_logging(settings.LOGGING)

        db.bind(**settings.DATABASE)
        db.generate_mapping(create_tables=True)

        scheduler = BlockingScheduler(
            executors=settings.EXECUTORS,
            timezone="Europe/Madrid"
        )

    except Exception as e:
        msg = "An error ocurred building massive_importer: %s"
        logger.exception(msg, e)
        raise e

    logger.debug("Build app finished")
    return scheduler


def add_jobs(app):
    tasks = Tasks()
    logger.debug("Adding task: %s", tasks.check_new_events.__name__)
    app.add_job(tasks.check_new_events, **settings.TASKS[tasks.check_new_events.__name__])
    logger.debug("Adding task: %s", tasks.web_crawling.__name__)
    app.add_job(tasks.web_crawling, **settings.TASKS[tasks.web_crawling.__name__])
    logger.debug("Adding task: %s", tasks.summary.__name__)
    app.add_job(tasks.summary, **settings.TASKS[tasks.summary.__name__])
