from collections import namedtuple
from datetime import datetime

from pony.orm import Database, Json, Required, PrimaryKey, Optional


db = Database()


class UpdateStatus(object):

    RDY_TO_PROCESS = 'ready'

    IN_PROCESS = 'in_process'

    WARNING = 'warning'

    ERROR = 'error'

    FINISHED = 'ok'


class Event(db.Entity):
    _table_ = 'events'

    key = PrimaryKey(str, auto=False)

    value = Required(Json)


class ImportFile(db.Entity):
    _table_ = 'import_file'

    id = PrimaryKey(int, auto=True)

    etag = Required(str, unique=True)

    bucket = Required(str)

    name = Required(str, index='index_importfile_name')

    portal = Optional(str)

    state = Required(
        str,
        default=UpdateStatus.RDY_TO_PROCESS,
        index='index_importfile_state'
    )

    size = Required(float)

    msg = Optional(str)

    created_at = Required(
        datetime,
        index='index_importfile_created_at',
        sql_default='CURRENT_TIMESTAMP'
    )

    modified_at = Required(
        datetime,
        index='index_importfile_modified_at',
        default=datetime.now
    )


class CrawlingProcessError(db.Entity):
    _table_ = 'crawling_process_error'

    id = PrimaryKey(int, auto=True)

    crawler_name = Required(str)

    exception_type = Optional(str)

    description = Optional(str)

    created_at = Required(
        datetime,
        index='index_crawlingprocess_created_at',
        sql_default='CURRENT_TIMESTAMP'
    )

    modified_at = Required(
        datetime,
        index='index_crawlingprocess_modified_at',
        default=datetime.now
    )
