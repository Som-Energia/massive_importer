# -*- coding: utf-8 -*-
from pickle import FALSE
import smtplib, urllib, datetime, ssl
from email import message
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

    def new_summary_send(self, date_events_task, i_date, f_date, event_list, importfile_list, errors_list):
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
                    'name' : event.metadata['portal'],
                    'success' : False,
                    'description': 'No s\'ha importat a l\'ERP'
                })
            for impf in importfile_list:
                correcte = impf.state == 'ok'
                import_file = {
                        'name' : urllib.parse.unquote(impf.name),
                        'success' : correcte,
                        'description': 'Importat correctament' if correcte else 'Hi ha hagut un error a l\'importar'
                }
                if correcte:
                    correcte.append(import_file)
                else:
                    fail.append(import_file)

            for error in errors_list:
                fail.append({
                    'name' : error.crawler_name,
                    'success' : False,
                    'description': error.exception_type + ': ' + error.description
                })

            plantilla = Template(filename='../../templates/daily_report.mako')
            render = plantilla.render(success = success, fail = fail, interval = interval)

            part1 = MIMEText(render, "html")
            message = MIMEMultipart("alternative")
            message.add_header('subject', "Resum importacio del dia " + i_date.strftime("%d-%m-%Y"))
            message.attach(part1)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.from_addr, self.passwd)
                server.sendmail(self.from_addr, self.to_addr, message.as_string())
                return True

    def summary_send(self, date_events_task, i_date, f_date, event_list, importfile_list, errors_list):
        def green_red_ok(state):
            if state == True: state = 'ok'
            if state == False: state = 'error'
            if(state=='ok'):
                return "<font color='#00ff00'>"+ state +"</font>"
            else:
                return "<font color='#FF0000'>"+ state +"</font>"
        def last_date(date):
            if date is None:
                return 'Data no disponible'
            else:
                return date.strftime("%Y-%m-%d %H:%M:%S")

        if i_date is None or f_date is None:
            raise TooFewArgumentsException('Too few arguments on summary send: dates missing')
        else:
            events = []; importfiles = []; errors = []
            for event in event_list : events.append(event.key)
            for impf in importfile_list : importfiles.append(urllib.parse.unquote(impf.name) + " < " + green_red_ok(impf.state) +" >")
            for error in errors_list : errors.append( "< " + green_red_ok('error') + " > " + error.crawler_name + ": " + error.exception_type + " --- " + error.description)

            _events = ""; _impfs = ""; _errors = ""
            if(events):
                _events = "<br><b>WARNING: Hi ha fitxers que no s'han importat al erp:</b><br>" + ("<br>".join(events)) +"<br>"
            if(importfiles):
                _impfs =  "Casos importats amb Estat: <br>" + ("<br>".join(importfiles)) +"<br>"
            if(errors):
                _errors =  "Errors durant la descàrrega de fitxers: <br>" + ("<br>".join(errors)) +"<br>"

            main_task = ("<b>RESUM DE DESCÀRREGA I IMPORTACIÓ AMB L'INTERVAL: " + i_date.strftime("%Y-%m-%d %H:%M:%S") + " fins el "+ f_date.strftime("%Y-%m-%d %H:%M:%S")) + "</b>"
            html = "<html><head></head><body>"+ main_task + "<br><br>" + _impfs + "<br>" + _errors + "<br>" + _events + "</body></html>"

            part1 = MIMEText(html, "html")
            message = MIMEMultipart("alternative")
            subject = "Resum importacio del dia " + i_date.strftime("%Y-%m-%d")
            message.add_header('subject', subject)
            message.attach(part1)
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
