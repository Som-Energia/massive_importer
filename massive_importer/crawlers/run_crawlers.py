import os
from twisted.internet import reactor
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
import logging
from massive_importer.crawlers.crawlers.spiders.iberdrola import Iberdrola
from massive_importer.crawlers.crawlers.spiders.endensa import Endesa

logger = logging.getLogger(__name__)
configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})

class WebCrawler:
    
    def __init__(self):
        settings_file_path = 'massive_importer.crawlers.crawlers.settings' # The path seen from root, ie. from main.py
        self.runner = CrawlerRunner()        

    def crawlIberdrola(self):
        logger.debug("Començo Iberdrola...")
        d = self.runner.crawl(Iberdrola)
        d.addBoth(lambda _: reactor.stop())
        reactor.run(installSignalHandlers=False) # the script will block here until the crawling is finished
        logger.debug("Acabo Iberdrola.")

    def crawlEndesa(self):
        pass
    
    # ...
    