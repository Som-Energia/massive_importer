import logging, scrapy, datetime, io, os
from massive_importer.lib import minio_utils
from massive_importer.lib.minio_utils import MinioManager
from massive_importer.conf import settings

logger = logging.getLogger(__name__)

minio_manager = MinioManager(**settings.MINIO, default_bucket="atr")

def run():
    return TestSpider

class TestSpider(scrapy.Spider):
    name = "testSpider"

    def start_requests(self):
        yield scrapy.Request(url="https://www.example.com", callback=self.download)

    def download(self, response):
        filename = "testSpider.zip"
        path = os.path.join(os.path.dirname(settings.ROOT_DIR), 'tests/data/', filename)
        todayfolder = datetime.datetime.now().strftime("%d-%m-%Y")
        filename = "%s/%s" % (todayfolder,filename)
        with open(path, 'rb') as content:
            data = content.read()
            minio_manager.put_file(minio_manager.default_bucket, filename, data)
