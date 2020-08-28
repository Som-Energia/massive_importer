from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from massive_importer.crawlers import all_creds
import logging, datetime, os, time
from massive_importer.lib import minio_utils
from massive_importer.lib.minio_utils import MinioManager
from massive_importer.conf import settings
from massive_importer.crawlers.crawlers.spiders.selenium_spiders import PortalConfig
from massive_importer.lib.exceptions import CrawlingProcessException, FileToBucketException


logger = logging.getLogger(__name__)
credentials = all_creds['endesa']

def instance():
    return Endesa()

class Endesa(PortalConfig):
    name='endesa'

    def wait_until_ready(self):
        while self.driver.find_element_by_id("00N2400000ILlcu_ileinner").text == 'En proceso':
            time.sleep(10)
            self.driver.refresh()

    def start(self):
        try:
            self.driver.get("https://portalede.endesa.es/login")
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.ID, "Login")))
            userbox = self.driver.find_element_by_id("username")
            userbox.send_keys(credentials['username'])
            passbox = self.driver.find_element_by_id("password")
            passbox.send_keys(credentials['password'])

            loginbt = self.driver.find_element_by_id("Login")
            loginbt.click()

            self.driver.get("https://portalede.endesa.es/apex/MessageDownload")

            inici = datetime.date(2019,1,4)
            final = datetime.date(2019,1,4)

            self.driver.switch_to_default_content()
            window_before = self.driver.window_handles[0]
            self.driver.execute_script("document.getElementById('j_id0:downloadForm:block:j_id34:j_id50:dowloadedFrom').setAttribute('value','{:%Y-%m-%d}')".format(inici))
            self.driver.execute_script("document.getElementById('j_id0:downloadForm:block:j_id34:j_id53:dowloadedTo').setAttribute('value','{:%Y-%m-%d}')".format(final))
            self.driver.execute_script("document.getElementById('j_id0:downloadForm:block:j_id34:j_id66:receivingCompany').setAttribute('value','0762')")

            sel = self.driver.find_element_by_id('j_id0:downloadForm:block:j_id34:j_id74:downloaded')
            for option in sel.find_elements_by_tag_name('option'):
                if option.text == 'Si':
                    option.click()
                    break

            self.driver.find_element_by_id("j_id0:downloadForm:block:downloadButtons:bottom:j_id7").click()
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.ID, "j_id0:downloadForm:block:resultsBlock:table:j_id83header:sortDiv")))
            self.driver.find_element_by_id("j_id0:downloadForm:block:downloadButtons:downloadAll").click()
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.ID, "j_id0:downloadForm:block:j_id8:j_id9:j_id10:0:j_id11:j_id12:j_id15")))

            self.driver.find_element(By.XPATH, "//a[@target='_blank']").click()
            time.sleep(5)
            window_after = self.driver.window_handles[1]

            self.driver.switch_to_window(window_after)
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.NAME, "download_messages")))
            self.wait_until_ready()
            self.driver.find_element_by_name("download_messages").click()

            filename = self.file_wait_download()

        except Exception as e:
            raise CrawlingProcessException(e)
        finally:
            self.driver.quit()
        try:
            newfilename = '{}_{}'.format(Endesa.name, filename)
            self.file_to_minio(filename, newfilename)
        except FileToBucketException as e:
            raise e
