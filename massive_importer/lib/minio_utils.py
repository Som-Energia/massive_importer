import logging
from minio import Minio
from minio.error import ResponseError


logger = logging.getLogger(__name__)


class MinioManager(object):

    def __init__(self, endpoint, access_key, secret_key, secure=False):
        self.minio_client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    def get_file_content(self, bucket, file_name):
        try:
            data = self.minio_client.get_object(bucket, file_name)
            content = data.read()

        except ResponseError as e:
            msg = "An error occurred getting content of %s from bucket %s: %s"
            logger.error(msg, file_name, bucket, e)
            content = ''
        finally:
            logger.debug('Longitud: %d', len(content))
            return content
