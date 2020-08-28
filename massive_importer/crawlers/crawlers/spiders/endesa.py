import scrapy, logging
from scrapy_splash import SplashRequest, SplashFormRequest
from massive_importer.crawlers import all_creds
import logging, scrapy, datetime, io, cgi
from massive_importer.crawlers.crawlers.items import zipItem
from massive_importer.lib import minio_utils
from massive_importer.lib.minio_utils import MinioManager
from massive_importer.conf import settings

logger = logging.getLogger(__name__)
minio_manager = MinioManager(**settings.MINIO)
credentials = all_creds['endesa']

def run():
    return Endesa()

class Endesa(scrapy.Spider):
    name = "endesa"

    def start_requests(self):
        urls = [
            'https://portalede.endesa.es/login',
        ]
        for url in urls:
            yield SplashRequest(url=url, callback=self.parse)

    def parse(self, response):

        data = {
            'un': credentials['username'],
            'width': '',
            'height': '',
            'hasRememberUn': '',
            'startURL': '',
            'loginURL': '',
            'loginType': '',
            'uneSecure': '',
            'local': '',
            'it': '',
            'qs': '',
            'locale': '',
            'oauth_token': '',
            'oauth_callback': '',
            'login': '',
            'serverid': '',
            'QCQQ': '',
            'display': '',
            'username': credentials['username'],
            'ExtraLog': str(response.xpath("//input[@name='ExtraLog']/@value").get()),
            'pw': credentials['password'],
            'Login' : '',
        }
        yield SplashFormRequest(url='https://portalede.endesa.es/login', formdata=data, callback=self.parse_html)

    def parse_html(self, response):
        # print ("************** Mostro l'html un cop loguejat: ***************")
        # print (response.xpath("/html").get())
        pass