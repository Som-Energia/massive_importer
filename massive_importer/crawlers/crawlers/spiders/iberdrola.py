from massive_importer.crawlers import all_creds
import logging, scrapy, datetime, io, cgi
from massive_importer.lib import minio_utils
from massive_importer.lib.minio_utils import MinioManager
from massive_importer.conf import settings

logger = logging.getLogger(__name__)
minio_manager = MinioManager(**settings.MINIO)
credentials = all_creds['iberdrola']

def run():
    return Iberdrola()

class Iberdrola(scrapy.Spider):
    name = "Iberdrola"
    
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
        now = datetime.datetime.now()
        today = now.strftime("%d/%m/%Y")
        base_form = {
            'accion': response.xpath("//input[@name='accion']/@value").get(),
            'fec_recep_desde': "13/05/2019",#today, # response.xpath("//input[@name='fec_recep_desde']/@value").get(),
            'hor_recep_desde': "00", # response.xpath("//input[@name='hor_recep_desde']/@value").get(),
            'min_recep_desde': "00", # response.xpath("//input[@name='min_recep_desde']/@value").get(),
            'seg_recep_desde': "00", # response.xpath("//input[@name='seg_recep_desde']/@value").get(),
            'fec_recep_hasta': "13/05/2019",#today, # response.xpath("//input[@name='fec_recep_hasta']/@value").get(),
            'hor_recep_hasta': "23", # response.xpath("//input[@name='hor_recep_hasta']/@value").get(),
            'min_recep_hasta': "59", # response.xpath("//input[@name='min_recep_hasta']/@value").get(),
            'seg_recep_hasta': "59", # response.xpath("//input[@name='seg_recep_hasta']/@value").get(),
            'fec_descarga_desde': response.xpath("//input[@name='fec_descarga_desde']/@value").get(),
            'hor_descarga_desde': response.xpath("//input[@name='hor_descarga_desde']/@value").get(),
            'min_descarga_desde': response.xpath("//input[@name='min_descarga_desde']/@value").get(),
            'seg_descarga_desde': response.xpath("//input[@name='seg_descarga_desde']/@value").get(),
            'fec_descarga_hasta': response.xpath("//input[@name='fec_descarga_hasta']/@value").get(),
            'hor_descarga_hasta': response.xpath("//input[@name='hor_descarga_hasta']/@value").get(),
            'min_descarga_hasta': response.xpath("//input[@name='min_descarga_hasta']/@value").get(),
            'seg_descarga_hasta': response.xpath("//input[@name='seg_descarga_hasta']/@value").get(),
            'tipo': response.xpath("//select[@name='tipo']/option[contains(text(),'Todos')]/@value").get(),
            'cod_emisora': "",
            'cod_destino': response.xpath("//select[@name='cod_emisora']/option[contains(text(), 'SOM ENERGIA')]/@value").get(),
            'des_emisora': response.xpath("//input[@name='des_emisora']/@value").get(),
            'cod_grupo_emp_emisora': response.xpath("//input[@name='cod_grupo_emp_emisora']/@value").get(),
            'cod_grupo_emp_destino': response.xpath("//input[@name='cod_grupo_emp_destino']/@value").get(),        
            'grupo_proceso': response.xpath("//select[@name='grupo_proceso']/option[@selected]/@value").get(),
            'cod_proceso': response.xpath("//select[@name='cod_proceso']/option[@selected]/@value").get(),
            'cod_paso': response.xpath("//select[@name='cod_paso']/option[@selected]/@value").get(),
            'cod_baja': response.xpath("//select[@name='cod_baja']/option[@selected]/@value").get(),
            'cod_solicitud': response.xpath("//input[@name='cod_solicitud']/@value").get(),
            'sec_solicitud': response.xpath("//input[@name='sec_solicitud']/@value").get(),
            'cups': response.xpath("//input[@name='cups']/@value").get(),
            'cod_descarga': response.xpath("//input[@name='cod_descarga']/@value").get(),
            'pagina': response.xpath("//input[@name='pagina']/@value").get(),
            'ventana': response.xpath("//input[@name='ventana']/@value").get(),
        }

        ServletConsultaMensajesDatos = {
            **base_form,
            'tipo_agente': response.xpath("//input[@name='tipo_agente']/@value").get(),
            'des_destino': response.xpath("//input[@name='des_destino']/@value").get(),
            'des_grupo_emp_emisora': response.xpath("//input[@name='des_grupo_emp_emisora']/@value").get(),
            'des_grupo_emp_destino': response.xpath("//input[@name='des_grupo_emp_destino']/@value").get(),
            'lista_cups': response.xpath("//input[@name='lista_cups']/@value").get(),
        }                                                                                                                                                                                                                                                                                                                                                                                         
        data = { **base_form , 'mensajes_firmados': "null"}

        yield scrapy.FormRequest(url='https://www.iberdrola.es/pwelconq/ServletConsultaMensajesDatos', 
                                 formdata=ServletConsultaMensajesDatos, 
                                 callback=self.step2, 
                                 meta={'base_form': base_form})

    def step2(self, response):
        yield scrapy.FormRequest(url='https://www.iberdrola.es/pwelconq/ServletConsultaMensajes', 
                                 formdata=response.meta.get('base_form'), 
                                 callback=self.step3, 
                                 meta={'base_form': response.meta.get('base_form')})

    def step3(self, response):
        pendents = int(response.xpath("//input[@name='numero']/@value").get())
            
        if pendents >= 1000 :
            logging.debug("Hi ha més del 1000 casos pendents!")
        elif not pendents:
            pass
        else:
            ServletListaMensajes = {
                **response.meta.get('base_form'),
                'mensajes_firmados':response.xpath("//input[@name='mensajes_firmados']/@value").get(),
                'lista_codigos_empresa_destino':response.xpath("//input[@name='lista_codigos_empresa_destino']/@value").get(),
                'lista_codigos_proceso':response.xpath("//input[@name='lista_codigos_proceso']/@value").get(),
                'fecha_desde':response.xpath("//input[@name='fecha_desde']/@value").get(),
                'fecha_hasta':response.xpath("//input[@name='fecha_hasta']/@value").get(),
                'usuario2':response.xpath("//input[@name='usuario2']/@value").get(),
                'estado':response.xpath("//input[@name='estado']/@value").get(),
                'fichero':response.xpath("//input[@name='fichero']/@value").get(),
                'numMens':response.xpath("//input[@name='numMens']/@value").get(),
                'Origen':response.xpath("//input[@name='Origen']/@value").get(),
                'operacion': "recibir", # response.xpath("//input[@name='operacion']/@value").get(),
                'n_mensaje': "", # response.xpath("//input[@name='n_mensaje']/@value").get(),
                'marcar_seleccion': "confimado", # response.xpath("//input[@name='marcar_seleccion']/@value").get(),
                'numero':response.xpath("//input[@name='numero']/@value").get(),
                'detalleTransferencia':response.xpath("//input[@name='detalleTransferencia']/@value").get(),
            }
            
            for i in range (0, pendents):
                cabecera = "cabecera"+str(i)
                ServletListaMensajes[cabecera] = response.xpath("//input[@name='"+cabecera+"']/@value").get()

            dictlist = []
            for key, value in ServletListaMensajes.items():
                temp = [key,value]
                dictlist.append(temp)

            for i in range (0, pendents): dictlist.append(['check', str(i)])      
        
            yield scrapy.FormRequest(url='https://www.iberdrola.es/pwelconq/ServletListaMensajes', 
                                     formdata=dictlist,
                                     callback=self.step4,)
    

    def step4(self, response):
        # logger.debug("************* Descarrega del fitxer zip ************" )
        try:
            filename = scrapy.utils.response.to_native_str(response.headers['Content-Disposition'])
            filename = filename.split(';')[1].split('=')[1]
            filename = filename.strip('"\'')
            todayfolder = datetime.datetime.now().strftime("%d-%m-%Y")
            full_filename = '{}_{}'.format(Iberdrola.name, filename)

            filename = "%s/%s" % (todayfolder,full_filename)
        except IndexError as err:
            logger.error(err)
        finally:
            yield minio_manager.put_file(minio_manager.default_bucket, filename, response.body)
        
    



    


