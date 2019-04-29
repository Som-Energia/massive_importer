import smtplib
from email import message
import logging
from unittest import TestCase
from massive_importer.conf.startup_configuration import settings

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
