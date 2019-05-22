from twisted.internet import reactor
import scrapy, logging, os, sys, importlib.util
from scrapy.crawler import CrawlerRunner
from massive_importer.conf import configure_logging, settings

logger = logging.getLogger(__name__)

class WebCrawler:
    def __init__(self):        
        self.crawlers = settings.CRAWLERS
        
    def crawl(self):
        runner = CrawlerRunner()
        path = os.path.dirname(os.path.abspath(__file__))
        spiders_path = os.path.join(path,"crawlers/spiders/")
        for spider in self.crawlers:
            if self.crawlers[spider]:
                try: 
                    spec = importlib.util.spec_from_file_location(spider, "".join([spiders_path,spider,'.py']))
                    imp = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(imp)
                    logger.debug("Loaded %s module" % (spider))
                except Exception as e:
                    logger.error("Can't import %s module" % (spider))
                finally:
                    logger.debug("Starting %s crawling..." % (spider))
                    runner.crawl(imp.instance())

        d = runner.join()
        d.addBoth(lambda _: reactor.stop())
        reactor.run(installSignalHandlers=False) # to run in the non-main thread
