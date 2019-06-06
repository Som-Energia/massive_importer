import smtplib
from email import message
import logging
import os, sys, json
from datetime import datetime
from unittest import TestCase
from pony.orm import db_session, sql_debug, count, select, set_sql_debug

os.environ.setdefault('MASSIVE_IMPORTER_SETTINGS', 'massive_importer.conf.envs.test')

from massive_importer.models.importer import Event, ImportFile, UpdateStatus, db
from massive_importer.conf import settings

logger = logging.getLogger(__name__)

class AlertTest(TestCase):

    @classmethod
    def setUpClass(cls): 
        cls.from_addr = settings.MAIL['from_address']
        cls.to_addr = settings.MAIL['to_address']
        cls.passwd = settings.MAIL['password']
        cls.server = smtplib.SMTP(settings.MAIL['host'], settings.MAIL['port'])
        cls.connectionResponse = cls.server.connect(settings.MAIL['host'], settings.MAIL['port'])
        cls.server.ehlo()
        cls.server.starttls()
        cls.server.ehlo()
        cls.loginResponse = cls.server.login(cls.from_addr, cls.passwd)
        

    def test_alert_send(self):
        self.assertEqual(self.connectionResponse[0], 220)
        self.assertTrue("Accepted" in self.loginResponse[1].decode("utf-8"))
        subject = 'Massive importer - Missatge de test!'
        body = 'Aquest missatge es llenca en executar el test de Alert de Massive importer'
        msg = message.Message()
        msg.add_header('from', self.from_addr)
        msg.add_header('to', self.to_addr)
        msg.add_header('subject', subject)
        msg.set_payload(body)   
        sendResponse = self.server.send_message(msg, from_addr=self.from_addr, to_addrs=[self.to_addr])
        self.assertEqual(sendResponse, {})
        self.server.quit()
    
    
    
    
    
    
    
    
    
    
    