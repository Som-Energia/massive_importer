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
credentials = all_creds['fenosa']

def instance():
    return Fenosa()

class Fenosa(PortalConfig):
    name='fenosa'

    def start(self):
        try:
            self.driver.get("https://sctd.gasnaturalfenosa.com/sctd/loginPage.do")
            userbox = self.driver.find_element_by_name("cdaLogin")
            userbox.send_keys(credentials['username'])
            passbox = self.driver.find_element_by_name("cdaPassword")
            passbox.send_keys(credentials['password'])

            loginbt = self.driver.find_element_by_id("bton")
            loginbt.click()

            inici = datetime.date(2019,6,12)
            final = datetime.date(2019,6,13)

            self.driver.switch_to_default_content()

            self.driver.execute_script(
                "document.getElementById('area_cliente').setAttribute('src','https://sctd.gasnaturalfenosa.com/sctd/elco/cons/descargaMensajesFiltrosElec.do')")
            originalWindows = [handle for handle in self.driver.window_handles ]
            self.driver.switch_to.frame(self.driver.find_element_by_name("area_cliente"))
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, 'fecMensajeDesde')))

            self.driver.execute_script("document.getElementById('fecMensajeDesde').setAttribute('value','{:%Y-%m-%d}')".format(inici))
            self.driver.execute_script("document.getElementById('fecMensajeHasta').setAttribute('value','{:%Y-%m-%d}')".format(final))
            self.driver.find_element_by_id("cdaEmisor_0022").click()
            self.driver.find_element_by_id("cdaEmisor_0390").click()

            self.driver.execute_script("consulta()")
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, 'gridgridDescargaMensajes')))
            self.driver.execute_script("seleccionar('seleccionarForm','gridDescargaMensajes','all','select_checkbox');")
            self.driver.execute_script("descargarGlobal();")

            filename = self.file_wait_download()

        except Exception as e:
            raise CrawlingProcessException(e)
        finally:
            self.driver.quit()
        try:
            newfilename = '{}_{}'.format(Fenosa.name, filename)
            self.file_to_minio(filename, newfilename)
        except Exception as e:
            raise FileToBucketException(e)
