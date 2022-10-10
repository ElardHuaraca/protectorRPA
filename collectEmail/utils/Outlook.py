from operator import contains
from webbrowser import get
from fileinput import filename
import datetime
import email
import imaplib
import environ
import pandas as pd


class Outlook():

    LOG_INFO = "OUTLOOK: "
    GET_ENV = environ.Env()

    def __init__(self) -> None:
        pass

    def login(self):
        self.email = Outlook.GET_ENV('EMAIL')
        self.password = Outlook.GET_ENV('PASSWORD')
        loggin_attempt = 0

        while True:
            try:
                self.imap = imaplib.IMAP4_SSL(Outlook.GET_ENV(
                    'IMAP_SERVER'), Outlook.GET_ENV('IMAP_PORT'))

                r, d = self.imap.login(self.email, self.password)
                assert r == 'OK', 'login failed: %s' % str(r)

                print(Outlook.LOG_INFO + "Accediendo como %s" % email, d)
                return
            except Exception as e:
                print(Outlook.LOG_INFO + "Error al iniciar sesion: %s" % str(e))

                loggin_attempt += 1
                if loggin_attempt > 3:
                    continue

                assert False, 'login failed'

    def readFolders(self, folder='Inbox'):
        return self.imap.select(folder)

    def sinceDate(self, days):
        date = datetime.datetime.now() - datetime.timedelta(days=days)
        return date.strftime('%d-%b-%Y')

    def readAllIdByDate(self, days=1):
        r, d = self.imap.search(
            None, '(SINCE "'+self.sinceDate(days)+'")', 'UNSEEN')
        return d[0].split(b' ')

    def getEmail(self, id):
        r, d = self.imap.fetch(id, '(RFC822)')
        assert r == 'OK', 'fetch failed: %s' % str(r)
        self.email_message = email.message_from_bytes(d[0][1])
        return

    def getBody(self):
        if self.email_message.is_multipart():
            body = {
                'message': self.email_message.get_payload(0),
                'attachment': self.email_message.get_payload(1, True)
            }
            return body
        else:
            body = {
                'message': self.email_message.get_payload(0),
                'attachment': None
            }
            return body

    def getMailByIdsAndFrom(self, ids):

        stack = {}

        if ids[0] == b'':
            return stack

        for id in ids:
            self.getEmail(id)
            if 'Data Protector Notification' in self.email_message['From'] and Outlook.GET_ENV('EMAIL') in self.email_message['To'] and ('link' in self.email_message['Subject'].lower() or 'schedule' in self.email_message['Subject'].lower()):
                subject = self.email_message['Subject'].replace('-', '')
                split_subject = subject.split(' ')

                if "" in split_subject:
                    split_subject.remove("")

                vcenter = split_subject[len(split_subject)-1]
                _type = 'schedule' if 'schedule' in [
                    x.lower() for x in split_subject] else 'link'

                if vcenter in stack:
                    stack[vcenter] = {
                        'schedule': self.getBody()['message'] if _type == 'schedule' else stack[vcenter]['schedule'],
                        'link': self.getBody()['message'] if _type == 'link' else stack[vcenter]['link']
                    }
                else:
                    stack[vcenter] = {
                        'schedule': self.getBody()['message'] if _type == 'schedule' else None,
                        'link': self.getBody()['message'] if _type == 'link' else None
                    }

        return stack
