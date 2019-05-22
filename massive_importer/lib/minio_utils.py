import logging, io
from minio import Minio
from minio.error import ResponseError


logger = logging.getLogger(__name__)


class MinioManager(object):

    def __init__(self, endpoint, access_key, secret_key, default_bucket, secure=False):
        self.default_bucket=default_bucket
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

    def put_file_content(self, bucket, file_name, data):
        try:
            self.minio_client.put_object(bucket, file_name, io.BytesIO(data), len(data))
        except ResponseError as e:
            msg = "An error occurred on put_file_content of %s from bucket %s: %s"
            logger.error(msg, file_name, bucket, e)
