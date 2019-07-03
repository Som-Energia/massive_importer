import os, logging
from unittest import TestCase
from minio import Minio
from minio.error import ResponseError
os.environ.setdefault('MASSIVE_IMPORTER_SETTINGS', 'massive_importer.conf.envs.test')
from massive_importer.conf import  settings
logger = logging.getLogger(__name__)
from . import testhelper

class TestMinioManager(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.bucket = testhelper.minio_manager.default_bucket
        testhelper.minio_manager.full_clean(cls.bucket)

    def test_put_file(self):
        file_name = 'test_file.zip'
        data = testhelper.get_content()
        ret = testhelper.minio_manager.put_file(self.bucket, file_name, data)
        self.assertTrue(ret)

    def test_list_objects(self):
        file_name = 'test_file.zip'
        data = testhelper.get_content()
        testhelper.minio_manager.put_file(self.bucket, file_name, data)

        full_list = testhelper.minio_manager.list_objects(self.bucket)
        for item in full_list:
            self.assertEqual(item.object_name, 'test_file.zip')

    def test_get_file_content(self):
        file_name = 'test_file.zip'
        data = testhelper.get_content()
        ret = testhelper.minio_manager.put_file(self.bucket, file_name, data)

        content = testhelper.minio_manager.get_file_content(self.bucket, file_name)
        self.assertEqual(content, testhelper.get_content())
        
    @classmethod
    def tearDownClass(self):
        testhelper.minio_manager.full_clean(self.bucket)
