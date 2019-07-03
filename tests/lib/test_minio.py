import os, logging
from unittest import TestCase
from minio import Minio
from minio.error import ResponseError
os.environ.setdefault('MASSIVE_IMPORTER_SETTINGS', 'massive_importer.conf.envs.test')
from massive_importer.conf import  settings
from massive_importer.lib.minio_utils import MinioManager
logger = logging.getLogger(__name__)


class TestMinioManager(TestCase):
    def setUp(self):
        self.minio_manager = MinioManager(**settings.MINIO, default_bucket='zips')
        self.minio_manager.full_clean('zips')
        
    def test_create_manager(self):
        self.assertNotEqual(None, self.minio_manager) 

    def test_put_and_get_file(self):
        file_name =  "prova.zip"
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/', file_name), 'rb') as f:
            data = f.read()
        try:
            self.minio_manager.put_file(self.minio_manager.default_bucket, file_name, data)
        except ResponseError as e:
            msg = "An error occurred on put_file_content of %s from bucket %s: %s"
            logger.error(msg, file_name, self.minio_manager.default_bucket, e)
        try:
            test_data = self.minio_manager.get_file_content(self.minio_manager.default_bucket, file_name)
        except ResponseError as e:
             msg = "An error occurred on get_file_content of %s from bucket %s: %s"
             logger.error(msg, file_name, self.minio_manager.default_bucket, e)
        self.assertEqual(test_data, data)

    def tearDown(self):
        self.minio_manager.full_clean('zips')