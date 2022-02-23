# -*- coding: utf-8 -*-
import smtplib, urllib, datetime, ssl
from email import message
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from massive_importer.lib.exceptions import TooFewArgumentsException
from mako.template import Template

import logging

logger = logging.getLogger(__name__)

class AlertManager(object):

    def __init__(self, from_address, to_address, password, host, port):
        self.from_addr = from_address
        self.to_addr = to_address
        self.passwd = password
        self.server = smtplib.SMTP(host, port)
        try:
            connectionResponse = self.server.connect(host, port)
            self.server.ehlo()
            self.server.starttls()
            self.server.ehlo()
            loginResponse = self.server.login(self.from_addr, self.passwd)
        except Exception as e:
            msg= "Error connecting to email server: %s"
            logger.error(msg, e)

    def alert_send(self, missatge, llistat):
        try:
            subject = 'Massive importer - Import Alert!'
            body = missatge + "\n" + ("\n".join(llistat))
            msg = message.Message()
            msg.add_header('from', self.from_addr)
            msg.add_header('to', self.to_addr)
            msg.add_header('subject', subject)
            msg.set_payload(body)
            sendResponse = self.server.send_message(msg, from_addr=self.from_addr, to_addrs=[self.to_addr])
            return True
        except Exception as e:
            logger.error("Error sending alert: %s", e)

    def summary_send(self, date_events_task, i_date, f_date, event_list, importfile_list, errors_list):
        if i_date is None or f_date is None:
            raise TooFewArgumentsException('Too few arguments on summary send: dates missing')
        else:
            interval = {
                'inici':i_date.strftime("%d-%m-%Y %H:%M:%S"),
                'final':f_date.strftime("%d-%m-%Y %H:%M:%S")
            }

            success = []
            fail = []

            for event in event_list:
                fail.append({
                    'name' : event.value['Records'][0]['s3']['object']['userMetadata']['X-Amz-Meta-Portal'],
                    'description': 'S\'ha descarregat però no s\'ha importat a l\'ERP [' +  event.key + ']'
                })
            for impf in importfile_list:
                correcte = impf.state == 'ok'
                import_file = {
                        'name' : impf.portal,
                        'description': 'Importat correctament' if correcte else ('S\'ha descarregat però hi ha hagut un error a l\'importar [' +  urllib.parse.unquote(impf.name) + ']')
                }
                if correcte:
                    success.append(import_file)
                else:
                    fail.append(import_file)

            for error in errors_list:
                fail.append({
                    'name' : error.crawler_name,
                    'description': error.description
                })

            plantilla = Template(filename='templates/daily_report.mako')
            render = plantilla.render(success = success, fail = fail, interval = interval)

            fp = open('templates/success.png', 'rb')
            success_img = MIMEImage(fp.read())
            fp.close()
            success_img.add_header('Content-ID', '<image1>')

            fp = open('templates/fail.png', 'rb')
            fail_img = MIMEImage(fp.read())
            fp.close()
            fail_img.add_header('Content-ID', '<image2>')

            part1 = MIMEText(render, "html")
            message = MIMEMultipart("alternative")
            message.add_header('subject', "Resum importacio del dia " + i_date.strftime("%d-%m-%Y"))
            message.attach(part1)
            message.attach(fail_img)
            message.attach(success_img)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.from_addr, self.passwd)
                server.sendmail(self.from_addr, self.to_addr, message.as_string())
                return True

    def close(self):
        try:
            self.server.quit()
        except Exception as e:
            raise
