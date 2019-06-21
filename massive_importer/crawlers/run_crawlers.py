from twisted.internet import reactor
import scrapy, logging, os, sys, importlib.util, logging
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from massive_importer.conf import configure_logging, settings
import threading, concurrent.futures

logger = logging.getLogger(__name__)

class WebCrawler:
    def __init__(self):        
        self.scrapy_crawlers = settings.SCRAPY_CRAWLERS
        self.selenium_crawlers = settings.SELENIUM_CRAWLERS

    def crawl(self):
        runner = CrawlerRunner()
        path = os.path.dirname(os.path.abspath(__file__))
        self.scrapy_spiders_path = os.path.join(path,"crawlers/spiders/")
        self.selenium_spiders_path = os.path.join(path,"crawlers/spiders/selenium_spiders/")

        for spider in self.scrapy_crawlers:
            try: 
                spec = importlib.util.spec_from_file_location(spider, "".join([self.scrapy_spiders_path,spider,'.py']))
                spider_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(spider_module)
                logger.debug("Loaded %s module" % (spider))
            except Exception as e:
                logger.error("Can't import %s module" % (spider))
            finally:
                logger.debug("Starting %s crawling..." % (spider))
                runner.crawl(spider_module.run())
        if self.scrapy_crawlers:
            d = runner.join()
            d.addBoth(lambda _: reactor.stop())
            reactor.run(installSignalHandlers=False) # to run in the non-main thread
        else:
            logger.debug("Any Scrapy Spider to crawl. ")

        if self.selenium_crawlers:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor: 
                crawl_list = {executor.submit(self.inicia, crawler): crawler for crawler in self.selenium_crawlers}     
                for future in concurrent.futures.as_completed(crawl_list): 
                    crwl = crawl_list[future] 
                    try: 
                        res = future.result() 
                    except Exception as e:
                        msg = "%r generated an exception: %s"
                        logger.exception(msg, crwl, e) 
                    else: 
                        logger.debug('%s generated with result: %r' % (crwl, res)) 
        else:
            logger.debug("Any Selenium Spider to crawl. ")


    def inicia(self, spider):
        # try: 
        spec = importlib.util.spec_from_file_location(spider, "".join([self.selenium_spiders_path,spider,'.py']))
        spider_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(spider_module)
        logger.debug("Loaded %s module" % (spider))
        # except Exception as e:
        #     logger.error("Can't import %s module" % (spider))
        # finally:
        logger.debug("Starting %s crawling..." % (spider))
        
        return spider_module.instance().start() 


class MockWebCrawler:
    def crawl(self):
        process =  CrawlerProcess()
        spider = "testSpider"
        try:
            path = os.path.dirname(os.path.abspath(__file__))
            spider_path = os.path.join(path,"crawlers/spiders/")
            spec = importlib.util.spec_from_file_location(spider, "".join([spider_path,spider,'.py']))
            imp = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(imp)
            process.crawl(imp.instance())
            process.start()
        except Exception as e:
            logger.error(e)
