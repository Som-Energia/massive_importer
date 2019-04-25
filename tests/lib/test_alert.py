import smtplib
from email import message
import logging
import os, sys, json
from datetime import datetime
from unittest import TestCase
from pony.orm import db_session, sql_debug, count, select, set_sql_debug

os.environ.setdefault('MASSIVE_IMPORTER_SETTINGS', 'massive_importer.conf.envs.test')

from massive_importer.models.importer import Event, ImportFile, UpdateStatus, db
from massive_importer.conf.startup_configuration import settings

logger = logging.getLogger(__name__)

class AlertTest(TestCase):

    @classmethod
    def setUpClass(cls): 
        from_addr = settings.MAIL['from_address']
        to_addr = settings.MAIL['to_address']
        passwd = settings.MAIL['password']
        server = smtplib.SMTP_SSL(settings.MAIL['host'], settings.MAIL['port'])
        server.login(from_addr, passwd)

    def test_alert_send(self):
        subject = 'I just sent this email from Python!'
        body = 'How neat is that?'
        msg = message.Message()
        msg.add_header('from', self.from_addr)
        msg.add_header('to', self.to_addr)
        msg.add_header('subject', subject)
        msg.set_payload(body)   
        self.server.send_message(msg, from_addr=self.from_addr, to_addrs=[self.to_addr])


    
    
    
    
    
    
    
    
    
    