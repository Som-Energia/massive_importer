from twisted.internet import reactor
import scrapy, logging, os, sys, importlib.util, datetime, re
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from massive_importer.conf import configure_logging, settings
import threading, concurrent.futures
from massive_importer.lib.minio_utils import MinioManager
from massive_importer.lib.exceptions import CrawlingProcessException, FileToBucketException, ModuleImportingException
from tests.lib import testhelper
logger = logging.getLogger(__name__)
class WebCrawler:
    def __init__(self):        
        self.scrapy_crawlers = settings.SCRAPY_CRAWLERS
        self.selenium_crawlers = settings.SELENIUM_CRAWLERS
        self.done_list = {}
        for elem in self.scrapy_crawlers: self.done_list[elem] = False
        for elem in self.selenium_crawlers: self.done_list[elem] = False

    def done_list(self):
        logger.error(self.done_list)
        return self.done_list

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
                logger.debug("Starting %s crawling..." % (spider))
                runner.crawl(spider_module.run())
            except Exception as e:
                logger.error("Can't import %s module" % (spider))
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
                        logger.debug('%s process done successfully with result: %r' % (crwl, res)) 
        else:
            logger.debug("Any Selenium Spider to crawl. ")

    def inicia(self, spider):
        try:
            spec = importlib.util.spec_from_file_location(spider, "".join([self.selenium_spiders_path,spider,'.py']))
            spider_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(spider_module)
            logger.debug("Loaded %s module" % (spider))
            logger.debug("Starting %s crawling..." % (spider))
            spider_module.instance().start() 
        except CrawlingProcessException as e:
            logger.error("***Error in Crawling process***: {}".format(spider))
            return False
        except FileToBucketException as e:
            logger.error("***Error uploading crawled file to Minio*** on {} process.".format(spider))
            return False
        except Exception as e:
            logger.error("Can't import %s module" % (spider))
            raise ModuleImportingException(e)
            return False
        else:
            return True

    def check_downloaded_files(self):
        minio_manager = MinioManager(**settings.MINIO)
        todayfolder = datetime.datetime.now().strftime("%d-%m-%Y")
        minio_manager = MinioManager(**settings.MINIO)
        prefix = "%s/" % (todayfolder)
        today_files = minio_manager.list_objects(minio_manager.default_bucket, prefix)
        name_list = []
        for item in today_files:
            distri = re.search('\/(.*?)\_', item.object_name).group(1)
            name_list.append(distri)
        for item in self.done_list: 
            self.done_list[item] = item in name_list

class MockWebCrawler:
    def __init__(self):        
        self.done_list = {}

    def crawl(self):
        file_name='test_file.zip'
        testhelper.put_file_in_bucket(file_name)
        
    def check_downloaded_files(self):
        self.done_list['testSpider'] = True 
