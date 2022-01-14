# -*- coding: utf-8 -*-
import argparse
import logging
from massive_importer.conf.startup_configuration import add_jobs, build_app

logger = logging.getLogger('massive_importer')


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-debug", "--debug", action='store_true', help="Enable debug mode")
    args = parser.parse_args()

    app = build_app(args)
    add_jobs(app)

    try:
        logger.info("Running massive importer...")
        app.start()
    except (KeyboardInterrupt, SystemError):
        logger.info("Stopping massive importer...")
        app.shutdown()
    except Exception as e:
        msg = "An uncontroled excepction occured: %s"
        logger.excepction(msg, e)


if __name__ == '__main__':
    main()
