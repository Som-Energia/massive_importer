import scrapy
import logging

logging.basicConfig(level=logging.DEBUG)

class HidroCantabrico(scrapy.Spider):
    name = "hc"

    def start_requests(self):
        urls = [
            'https://webgia.eredesdistribucion.es/AGEN/inicio',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # logging.debug("************** Mostro headers a la primera connexio ***************")
        # logging.debug(response.request.headers)
        # logging.debug(response.xpath("/html").get())
        pass
