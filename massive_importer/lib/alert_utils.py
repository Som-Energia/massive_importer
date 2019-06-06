import smtplib, urllib, datetime, ssl
from email import message
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
        subject = 'Massive importer - Import Alert!'
        body = missatge + "\n" + ("\n".join(llistat))
        msg = message.Message()
        msg.add_header('from', self.from_addr)
        msg.add_header('to', self.to_addr)
        msg.add_header('subject', subject)
        msg.set_payload(body)   
        sendResponse = self.server.send_message(msg, from_addr=self.from_addr, to_addrs=[self.to_addr])
        self.server.quit()

    def summary_send(self, i_date, f_date, event_list, importfile_list):
        def green_red_ok(state):
            if(state=='ok'): 
                return "<font color='#00ff00'>"+ state +"</font>"
            else: 
                return "<font color='#FF0000'>"+ state +"</font>"
        events = []; importfiles = []
        for event in event_list : events.append(event.key)
        for impf in importfile_list : importfiles.append(urllib.parse.unquote(impf.name) + " < " + green_red_ok(impf.state) +" >")
        _events = ""; _impfs = ""
        if(events):
            _events = "Casos pendents d'importar: <br>" + ("<br>".join(events)) +"<br>"
        if(importfiles):
            _impfs =  "Casos importats amb Estat: <br>" + ("<br>".join(importfiles)) +"<br>" 
        text = "Resum importacio del dia " + i_date.strftime("%Y-%m-%d %H:%M:%S") + " fins el "+ f_date.strftime("%Y-%m-%d %H:%M:%S") + "<br><br>"
        html = "<html><head></head><body>"+ text + _events + "<br>" + _impfs + "</body></html>"
        part1 = MIMEText(html, "html")
        message = MIMEMultipart("alternative")
        subject = "Resum importacio del dia " + i_date.strftime("%Y-%m-%d")
        message.add_header('subject', subject)
        message.attach(part1)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(self.from_addr, self.passwd)
            server.sendmail(self.from_addr, self.to_addr, message.as_string())
        self.server.quit()
