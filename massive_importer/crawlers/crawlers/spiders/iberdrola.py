from massive_importer.crawlers import iberdrola_cred as credentials
import logging
import scrapy


class Iberdrola(scrapy.Spider):
    name = "iberdrola"

    def start_requests(self):
        urls = [
            'https://www.iberdrola.es/pwmultid/ServletAutentificacion?pwmultid=iberdrolad',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        data = {
            'accion': response.xpath("//input[@name='accion']/@value").get(),
            'distribuidora': response.xpath("//input[@name='distribuidora']/@value").get(),
            'usuario': credentials['username'],
            'clave': credentials['password'],
        }
        yield scrapy.FormRequest(url='https://www.iberdrola.es/pwmultid/ServletLogin', formdata=data, callback=self.parse_html)

    def parse_html(self, response):
        yield scrapy.Request(url='https://www.iberdrola.es/pwelconq/ServletOpcion?opcion=0021_MENSA_CONSULTAMENSAJES', callback=self.seguiment)

    def seguiment(self, response):
        dataDatos = {
            'accion': response.xpath("//input[@name='accion']/@value").get(),
            'pagina': "0",
            'ventana': "1000",
            'tipo_agente': "",
            'fec_recep_desde': response.xpath("//input[@id='fec_recep_desde']/@value").get(),
            'hor_recep_desde': response.xpath("//input[@id='hor_recep_desde']/@value").get(),
            'min_recep_desde': response.xpath("//input[@id='min_recep_desde']/@value").get(),
            'seg_recep_desde': response.xpath("//input[@id='seg_recep_desde']/@value").get(),

            'fec_recep_hasta': response.xpath("//input[@id='fec_recep_hasta']/@value").get(),
            'hor_recep_hasta': response.xpath("//input[@id='hor_recep_hasta']/@value").get(),
            'min_recep_hasta': response.xpath("//input[@id='min_recep_hasta']/@value").get(),
            'seg_recep_hasta': response.xpath("//input[@id='seg_recep_hasta']/@value").get(),
            
            'fec_descarga_desde': "",
            'hor_descarga_desde': "",
            'min_descarga_desde': "",
            'seg_descarga_desde': "",
            'fec_descarga_hasta': "",
            'hor_descarga_hasta': "",
            'min_descarga_hasta': "",
            'seg_descarga_hasta': "",
            'cod_emisora':        "",
            'cod_destino': response.xpath("//select[@name='cod_destino']/option[contains(text(),'SOM ENERGIA')]/@value").get(),
            'des_destino': "",
            'des_emisora': "",
            'cod_grupo_emp_emisora': "",
            'cod_grupo_emp_destino': "",
            'des_grupo_emp_emisora': "",
            'des_grupo_emp_destino': "",
            'grupo_proceso': "S",
            'cod_proceso': "S",
            'cod_paso': "S",
            'cod_baja': "S",
            'cod_solicitud': "",
            'sec_solicitud': "",
            'cups': "",
            'tipo': "Correctos",
            'lista_cups': "",
            'cod_descarga': "",
        }
      
        data = {
            'accion': 'cargar',
            'fec_recep_desde': "13/05/2019",
            'hor_recep_desde': response.xpath("//input[@id='hor_recep_desde']/@value").get(),
            'min_recep_desde': response.xpath("//input[@id='min_recep_desde']/@value").get(),
            'seg_recep_desde': response.xpath("//input[@id='seg_recep_desde']/@value").get(),
            'fec_recep_hasta': "13/05/2019",
            'hor_recep_hasta': response.xpath("//input[@id='hor_recep_hasta']/@value").get(),
            'min_recep_hasta': response.xpath("//input[@id='min_recep_hasta']/@value").get(),
            'seg_recep_hasta': response.xpath("//input[@id='seg_recep_hasta']/@value").get(),
            'fec_descarga_desde': "",
            'hor_descarga_desde': "",
            'min_descarga_desde': "",
            'seg_descarga_desde': "",
            'fec_descarga_hasta': "",
            'hor_descarga_hasta': "",
            'min_descarga_hasta': "",
            'seg_descarga_hasta': "",
            'tipo': "Correctos",
            'cod_emisora':        "",
            'cod_destino': response.xpath("//select[@name='cod_destino']/option[contains(text(),'SOM ENERGIA')]/@value").get(),
            'cod_grupo_emp_emisora': "",
            'cod_grupo_emp_destino': "",
            'grupo_proceso': "S",
            'cod_proceso': "S",
            'cod_paso': "S",
            'cod_baja': "S",
            'cod_solicitud': "",
            'sec_solicitud': "",
            'cups': "",
            'cod_descarga': "",
            'mensajes_firmados': "null",
            'pagina': "0",
            'ventana': "1000",
            
        }
        # for x in dataDatos: print(x, ":", dataDatos[x])
        yield scrapy.FormRequest(url='https://www.iberdrola.es/pwelconq/ServletConsultaMensajesDatos', formdata=dataDatos, callback=self.step2, meta={'dades': data} )

    def step2(self, response):
        # for x in response.meta.get('dades'): print(x, ":", response.meta.get('dades')[x])
        yield scrapy.FormRequest(url='https://www.iberdrola.es/pwelconq/ServletConsultaMensajes', formdata=response.meta.get('dades'), callback=self.step3)

    def step3(self, response):
        # logging.debug("************* Mostro l'html despres de filtrar ************" )
        logging.debug(response.xpath("/html").get())

