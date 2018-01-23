import os
from unittest import TestCase

from minio import Minio
from minio.error import ResponseError

os.environ.setdefault('MASSIVE_IMPORTER_SETTINGS', 'massive_importer.conf.envs.test')

from massive_importer.conf import configure_logging, settings
from massive_importer.lib.minio_utils import MinioManager


class TestMinioManager(TestCase):

    file_name = 'es.csv'
    bucket = 'test'

    def setUp(self):
        configure_logging(settings.LOGGING)
        self.minio_client = Minio(**settings.MINIO)
        self.minio_manager = MinioManager(**settings.MINIO)

    def test_create_manager(self):
        self.assertNotEqual(None, self.minio_manager)

    def test_get_file(self):
        try:
            test_data = self.minio_client.get_object(self.bucket, self.file_name).read()
        except ResponseError:
            test_data = ''

        data = self.minio_manager.get_file_content(self.bucket, self.file_name)

        self.assertEquals(test_data, data)
