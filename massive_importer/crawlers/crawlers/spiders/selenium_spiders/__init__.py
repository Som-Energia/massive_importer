
import os, time, glob, datetime, logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from massive_importer.lib.minio_utils import MinioManager
from massive_importer.conf import settings
from massive_importer.lib.exceptions import FileToBucketException

minio_manager = MinioManager(**settings.MINIO)
logger = logging.getLogger(__name__)

class PortalConfig(object):
    def __init__(self) :
        options = Options()
        # options.add_argument('--headless')

        self.targetDirectory = os.path.join(os.path.dirname(os.path.abspath(__file__)),'tmp/')
        profile = webdriver.FirefoxProfile()
        profile.set_preference('browser.download.folderList', 2)
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        profile.set_preference('browser.download.dir', self.targetDirectory)
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/zip, application/octet-stream, application/x-zip-compressed, multipart/x-zip, application/x-rar-compressed, application/octet-stream')
        self.driver = webdriver.Firefox(profile, options=options, log_path='/dev/null')

    def file_wait_download(self):
        os.chdir(self.targetDirectory)
        files_count = len(glob.glob('*'))
        # Waiting download to start
        time.sleep(10)
        # Checking if downloaded
        while glob.glob('*.part') or len(glob.glob('*')) == files_count:
            time.sleep(5)
        filename = max([f for f in os.listdir(self.targetDirectory)], key=os.path.getctime)
        return filename
    
    def file_to_minio(self, filename, newfilename=None, removeFile=True):
        if newfilename == None:
            newfilename = filename
        full_path = os.path.join(self.targetDirectory, filename)
        todayfolder = datetime.datetime.now().strftime("%d-%m-%Y")
        filename = "%s/%s" % (todayfolder,newfilename)
        try: 
            with open(full_path, 'rb') as content:
                data = content.read()
                minio_manager.put_file(minio_manager.default_bucket, filename, data)                 
        except Exception as e:
            raise FileToBucketException(e)
        finally:
            if removeFile: os.remove(full_path)
