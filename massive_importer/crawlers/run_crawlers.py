from twisted.internet import reactor
import scrapy
import logging
import os
import sys
import importlib
import datetime
import re
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from massive_importer.conf import configure_logging, settings
from massive_importer.lib.db_utils import insert_crawling_process_error
import threading
import concurrent.futures
from massive_importer.lib.minio_utils import MinioManager
from massive_importer.lib.exceptions import CrawlingProcessException, FileToBucketException, CrawlingLoginException
from tests.lib.testhelper import TestHelper
logger = logging.getLogger(__name__)


class WebCrawler:
    def __init__(self):
        self.MAX_RETRIES = 5
        self.minio_manager = MinioManager(**settings.MINIO)
        self.scrapy_crawlers = settings.SCRAPY_CRAWLERS
        self.selenium_crawlers = settings.SELENIUM_CRAWLERS
        self.scrapy_crawlers_conf = settings.SCRAPY_CRAWLERS_CONF
        self.selenium_crawlers_conf = settings.SELENIUM_CRAWLERS_CONF
        self.done_list = {}
        for elem in self.scrapy_crawlers:
            self.done_list[elem] = False
        for elem in self.selenium_crawlers:
            self.done_list[elem] = False

    def done_list(self):
        logger.error(self.done_list)
        return self.done_list

    def crawl(self):
        runner = CrawlerRunner()
        path = os.path.dirname(os.path.abspath(__file__))
        self.scrapy_spiders_path = os.path.join(path, "crawlers/spiders/")
        self.selenium_spiders_path = os.path.join(
            path, "crawlers/spiders/selenium_spiders/")

        for spider in self.scrapy_crawlers:
            try:
                spec = importlib.util.spec_from_file_location(
                    spider, "".join([self.scrapy_spiders_path, spider, '.py']))
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
            # to run in the non-main thread
            reactor.run(installSignalHandlers=False)
        else:
            logger.debug("No Scrapy Spider to crawl. ")

        if self.selenium_crawlers:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                futures = {}
                execution_counter = {key: 0 for key in self.selenium_crawlers}
                while self.selenium_crawlers:
                    for crawler in self.selenium_crawlers:
                        futures[crawler] = (
                            executor.submit(self.inicia, crawler))

                    for crawler, future in futures.items():
                        execution_counter[crawler] += 1
                        result = future.result()
                        retry = result['retry']
                        if result['has_error']:
                            exception = result['exception']
                            retry_msg = '(attempt {})'.format(
                                execution_counter[crawler]) if execution_counter[crawler] else ''
                            logger.error(
                                "**EXCEPTION** {}: {} generated: {}".format(retry_msg, crawler, str(exception)))
                            insert_crawling_process_error(crawler, exception)
                            if retry:
                                logger.debug(
                                    '%s added for a retry.' % (crawler))
                            else:
                                self.selenium_crawlers.remove(crawler)
                        else:
                            logger.debug(
                                '%s process done successfully!' % (crawler))
                            self.selenium_crawlers.remove(crawler)

                        if execution_counter[crawler] >= self.MAX_RETRIES:
                            self.selenium_crawlers.remove(crawler)

                    if self.selenium_crawlers:
                        logger.info(
                            "Starting Selenium retry queue in 30 seconds...")
                        time.sleep(30)
        else:
            logger.debug("No Selenium Spider to crawl. ")

    def inicia(self, spider):
        try:
            spec = importlib.util.spec_from_file_location(
                spider, "".join([self.selenium_spiders_path, spider, '.py']))
            spider_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(spider_module)
            logger.debug("Loaded %s module" % (spider))
            logger.debug("Starting %s crawling..." % (spider))
            spider_instance = spider_module.instance(
                self.selenium_crawlers_conf[spider])
            spider_instance.start_with_timeout()
        except CrawlingLoginException as e:
            return({'has_error': True, 'exception': e, 'retry': False})
        except CrawlingProcessException as e:
            return({'has_error': True, 'exception': e, 'retry': True})
        except FileToBucketException as e:
            return({'has_error': True, 'exception': e, 'retry': True})
        except Exception as e:
            return({'has_error': True, 'exception': e, 'retry': True})
        else:
            return({'has_error': False, 'retry': False})

    def check_downloaded_files(self):
        todayfolder = datetime.datetime.now().strftime("%d-%m-%Y")
        prefix = "%s/" % (todayfolder)
        today_files = self.minio_manager.list_objects(
            self.minio_manager.default_bucket, prefix)
        name_list = []
        for item in today_files:
            match = re.search('\/(.*?)\_', item.object_name)
            if match:
                distri = match.group(1)
                name_list.append(distri)
            elif 'testSpider' in item.object_name:
                name_list.append('testSpider')
            else:
                name_list.append(item.object_name)
        for item in self.done_list:
            self.done_list[item] = item in name_list


class MockWebCrawler:
    def __init__(self):
        self.done_list = {}
        self.minio_manager = MinioManager(**settings.MINIO)

    def crawl(self):
        file_name = 'test_file.zip'
        TestHelper.put_file_in_bucket(self, file_name)

    def check_downloaded_files(self):
        self.done_list['testSpider'] = True
