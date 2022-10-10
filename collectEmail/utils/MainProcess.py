from collectEmail.utils.Outlook import Outlook
from collectEmail.models import UltimateVerification
from django.utils import timezone
from openpyxl import load_workbook
import pandas as pd


class MainProcessCollect():

    def __init__(self):
        self.start_collect()

    def start_collect(self):
        outlook = Outlook()
        outlook.login()
        outlook.readFolders()
        ids = outlook.readAllIdByDate(days=2)
        mails = outlook.getMailByIdsAndFrom(ids)
        self.wait_more_emails(mails)

    def check_hours_passed(self, time):
        new = time.comprovate + timezone.timedelta(hours=2)
        now = timezone.now()
        return now >= new

    def wait_more_emails(self, mails):
        time = UltimateVerification.objects.all().first()

        if time is None:
            if len(mails) == 0:
                return
            self.process_mails(mails)

        else:
            if self.check_hours_passed(time) and len(mails) == 0:
                self.send_report_link()
                return
            elif not self.check_hours_passed(time):
                self.process_mails(mails, time)
            else:
                self.process_mails(mails, time)
                self.send_report_link()

    def saveFirstFile():
        writer = pd.ExcelWriter('report.xlsx', engine='xlsxwriter')
        writer.save()

    def process_mails(self, mails, time=None):
        if time is None:
            time = UltimateVerification.objects.create()
            time.save()

        for key, mail in mails.items():
            if mail['schedule'] is None:
                continue

            string_body = mail['schedule'].as_string()
            table = pd.read_html(string_body)

            wb = load_workbook('report.xlsx')

            writer = pd.ExcelWriter('report.xlsx', engine='xlsxwriter')
            writer.book = wb
            table[0].to_excel(writer, sheet_name=key)
            writer.save()

        if len(mails) > 0:
            time.comprovate = timezone.now()
            time.save()

    def send_report_link(self):
        print('send report link')
        return
