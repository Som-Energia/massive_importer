import os, logging
from unittest import TestCase
from minio import Minio
from minio.error import ResponseError
os.environ.setdefault('MASSIVE_IMPORTER_SETTINGS', 'massive_importer.conf.envs.test')
from massive_importer.conf import  settings
logger = logging.getLogger(__name__)
from . import test_helper

class TestMinioManager(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.bucket = test_helper.minio_manager.default_bucket
        test_helper.minio_manager.full_clean(cls.bucket)

    def test_put_file(self):
        file_name = 'test_file.zip'
        data = test_helper.get_content()
        ret = test_helper.minio_manager.put_file(self.bucket, file_name, data)
        self.assertTrue(ret)

    def test_list_objects(self):
        file_name = 'test_file.zip'
        data = test_helper.get_content()
        test_helper.minio_manager.put_file(self.bucket, file_name, data)

        full_list = test_helper.minio_manager.list_objects(self.bucket)
        for item in full_list:
            self.assertEqual(item.object_name, 'test_file.zip')

    def test_get_file_content(self):
        file_name = 'test_file.zip'
        data = test_helper.get_content()
        ret = test_helper.minio_manager.put_file(self.bucket, file_name, data)

        content = test_helper.minio_manager.get_file_content(self.bucket, file_name)
        self.assertEqual(content, test_helper.get_content())
        
    @classmethod
    def tearDownClass(self):
        test_helper.minio_manager.full_clean(self.bucket)
