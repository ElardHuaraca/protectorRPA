import datetime
import email
import imaplib
import sys
from pydoc import doc
from collectEmail import config


class MainProcessCollect():

    mails = {}

    def __init__(self):
        self.start_collect()

    def start_collect(self):
        self.login()
        self.readInbox()
        list = self.readIdsToday()
        self.getMailByIdsAndWord(list, " ")

    def login(self):
        email = config.email
        password = config.password
        login_attempt = 0
        while True:
            try:
                self.imap = imaplib.IMAP4_SSL(
                    config.IMAP_SERVER, config.IMAP_PORT)
                r, d = self.imap.login(email, password)
                assert r == 'OK', 'login failed: %s' % str(r)
                print("> Accediendo como %s" % email, d)
                return
            except Exception as e:
                print("> Error al iniciar sesion: %s" % str(e))
                login_attempt += 1
                if login_attempt > 3:
                    continue
                assert False, 'login failed'

    """ read inbox outlook """

    def readInbox(self):
        r, d = self.imap.select('INBOX')
        assert r == 'OK', 'select failed: %s' % str(r)
        print("> Accediendo a la bandeja de entrada")
        return d
        return self.imap.select('Inbox', readonly=True)

    def sinceToday(self, days):
        date = datetime.datetime.now() - datetime.timedelta(days=days)
        print(date.strftime("%d-%b-%Y"))
        return date.strftime('%d-%b-%Y')

    def readIdsToday(self):
        """ get emails btween dates """
        """ r, d = self.imap.search(None, '(SINCE "%s")' % self.sinceToday(1))
        assert r == 'OK', 'search failed: %s' % str(r)
        ids = d[0].split()
        print("> Emails encontrados: %s" % len(ids))
        return ids """
        r, d = self.imap.search(
            None, '(SINCE "'+self.sinceToday(1)+'")', 'UNSEEN')
        list = d[0].split(b' ')
        print("> Emails no leidos: %s" % len(list))
        return list

    def getMailByIdsAndWord(self, ids, word):
        stack = []
        for id in ids:
            self.getEmail(id)
            print("> Content %s" % self.getBody())
            """ if word in self.getBody().lower():
                stack.append(self.email_message) """
        return stack

    """ get email from outlook by id """

    def getEmail(self, id):
        r, d = self.imap.fetch(id, '(RFC822)')
        assert r == 'OK', 'fetch failed: %s' % str(r)
        self.email_message = email.message_from_bytes(d[0][1])
        return self.email_message

    """ get email body and detect is multipart  """

    def getBody(self):
        """ print remiten """
        print(self.email_message['From'])
        """ print subject """
        print(self.email_message['Subject'])
        """ print date """
        print(self.email_message['Date'])
        """ if self.email_message.is_multipart():
            for payload in self.email_message.get_payload():
                if payload.get_content_type() == 'text/plain':
                    return payload.get_payload()
        else:
            return self.email_message.get_payload(None, True) """

        old_stdout = sys.stdout
        log_file = open("log.txt", "w")
        sys.stdout = log_file
        print("> msm %s" % self.email_message.get_payload()[0])
        print(self.email_message['From'])
        sys.stdout = old_stdout
        log_file.close()
        if self.email_message.is_multipart():
            for payload in self.email_message.get_payload():
                body = (
                    payload.get_payload(0)
                )
                return body
        else:
            body = (
                self.email_message.get_payload(None, True)
            )
            return body
