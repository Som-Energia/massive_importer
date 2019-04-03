from collections import namedtuple
from datetime import datetime

from pony.orm import Database, Json, Required, PrimaryKey, Optional


db = Database()


class UpdateStatus(object):

    RDY_TO_PROCESS = 'ready'

    IN_PROCESS = 'in_process'

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

    name = Required(str, index='index_importfile_name')

    state = Required(
        str,
        default=UpdateStatus.RDY_TO_PROCESS,
        index='index_importfile_state'
    )

    size = Required(float)

    retries = Required(int, default=0)

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
