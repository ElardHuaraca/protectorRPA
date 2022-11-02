from calendar import c
from itertools import count
import os
import re
from turtle import left
from automationDataProtector import settings
from collectEmail.utils.Outlook import Outlook
from collectEmail.models import Email, ScheduleOrLink, UltimateVerification
from django.utils import timezone
from openpyxl import load_workbook, Workbook
import pandas as pd
import environ


class MainProcessCollect():

    GET_ENV = environ.Env()

    def __init__(self):
        self.start_collect()

    def start_collect(self):
        self.outlook = Outlook()
        self.outlook.login()
        self.outlook.readFolders()
        ids = self.outlook.readAllIdByDate(days=2)
        mails = self.outlook.getMailByIdsAndFrom(ids)
        self.wait_more_emails(mails)

    """ first request create file to write items for Link """

    def saveFirstFile(name):
        """ Verify file exist """
        if not os.path.exists(name):
            """ Save Report file """
            workbook = Workbook()

            sheet = workbook.active
            sheet["A1"] = "Hello"
            sheet["B1"] = "World!"

            workbook.save(filename=name)
            workbook.close()

    """ wait more emails if 2 hours not passed, it's over check if more emails exits or not and send email with link """

    def wait_more_emails(self, mails):
        time = UltimateVerification.objects.all().first()

        if time is None and len(mails) > 0:
            self.process_mails(mails)
        elif time is not None:
            if self.check_hours_passed(time) and len(mails) == 0:
                self.send_report_link()
            elif not self.check_hours_passed(time):
                self.process_mails(mails, time)
            else:
                self.process_mails(mails, time)
                self.send_report_link()

    """ verify hour passed is 2 hours or not"""

    def check_hours_passed(self, time):
        new = time.comprovate + timezone.timedelta(hours=1)
        now = timezone.now()
        return now >= new

    def process_mails(self, mails, time=None):
        self.mails_len = len(mails)

        for key, mail in mails.items():
            self.save_time(time)
            self.key_ = key

            if mail['schedule'] is not None and mail['link'] is None:
                link = self.get_email_saved()
                if link is not None:
                    return self.apply_filters(mail['schedule'], link.body)
                else:
                    self.save_email_body(mail, 'schedule')
                    continue

            elif mail['schedule'] is None and mail['link'] is not None:
                schedule = self.get_email_saved()
                if schedule is not None:
                    return self.apply_filters(schedule.body, mail['link'])
                else:
                    self.save_email_body(mail, 'link')
                    continue
            else:
                return self.apply_filters(mail['schedule'], mail['link'])

    """ send email with link and delete all sheets in excel file """

    def send_report_link(self):
        email = Email.objects.all().first()

        if email is not None:

            self.deleteSheet(self.GET_ENV('FILE_1'), 'Sheet')
            self.deleteSheet(self.GET_ENV('FILE_2'), 'Sheet')
            self.deleteSheet(self.GET_ENV('FILE_3'), 'Sheet')
            self.deleteSheet(self.GET_ENV('FILE_4'), 'Sheet')
            self.deleteSheet(self.GET_ENV('FILE_5'), 'Sheet')

            state_send = self.outlook.send_mail(
                to=email.email, subject='Reportes para hacer el LINK',)
            if state_send:

                """ delete all files .xlsx """
                self.delete_files()

                """ delete time saved """
                time = UltimateVerification.objects.all().first()
                time.delete()

    print('function_send email with link')

    """ save time if time to verify is time passed 2 hours or send email with link """

    def save_time(self, time=None):
        if time is None:
            time = UltimateVerification.objects.create()
            time.save()
        else:
            if self.mails_len > 0:
                time.comprovate = timezone.now()
                time.save()

    """ Consult email body with id server  """

    def get_email_saved(self):
        return ScheduleOrLink.objects.filter(id=self.key_).first()

    """ Save email body when schedule or link is None for after process """

    def save_email_body(self, mail, type):
        ScheduleOrLink.objects.create(
            id=self.key_, body=mail[type].as_string(), type=type).save()

    """ Apply filters to schedule and link and write excel"""

    def apply_filters(self, schedule, link):
        schedule_ = schedule if isinstance(
            schedule, str) else schedule.as_string()
        link_ = link if isinstance(link, str) else link.as_string()

        self.table_schedule = pd.read_html(schedule_)
        self.table_link = pd.read_html(link_)

        self.table_schedule[0].sort_values(by=['Specification'], inplace=True)
        self.table_link[0].sort_values(by=['Specification'], inplace=True)

        self.check_query_and_apply_filter(
            "Specification.str.contains('(?i)dia')")
        self.check_query_and_apply_filter(
            "Specification.str.contains('(?i)dem|demanda')")
        self.check_query_and_apply_filter(
            "Specification.str.contains('(?i)crq')")
        self.check_query_and_apply_filter(
            "Specification.str.contains('(?i)rfc')")
        self.check_query_and_apply_filter("Group.isna()")
        self.check_query_and_apply_filter("Group.str.contains('(?i)apagado')")
        self.check_query_and_apply_filter("Group.str.contains('(?i)migrado')")
        self.check_query_and_apply_filter("Group.str.contains('(?i)de baja')")
        self.check_query_and_apply_filter(
            "Group.str.contains('(?i)desactivado_temporalmente')")
        self.check_query_and_apply_filter("Group.str.contains('(?i)test')")
        self.check_query_and_apply_filter("Group.str.contains('(?i)migrado')")
        self.check_query_and_apply_filter(
            "Group.str.contains('(?i)historicos')")
        self.check_query_and_apply_filter("Group.str.len() < 1")
        self.check_query_and_apply_filter(
            "`Session Type`.str.contains('(?i)copy')")

        self.replace_string_into_column('(?i)mssql', '', 'Specification')
        self.replace_string_into_column('(?i)veagent', '', 'Specification')
        self.replace_string_into_column('(?i)hana', '', 'Specification', 1)
        self.replace_string_into_column('(?i)sap', '', 'Specification', 1)
        self.replace_string_into_column('(?i)oracle8', '', 'Specification')
        self.replace_string_into_column('(?i)idb', '', 'Specification', 1)
        self.replace_string_into_column('(?i)sybase', '', 'Specification', 1)

        self.delete_schedule_items_with_status(
            "Status.str.contains('(?i)aborted')")
        self.delete_schedule_items_with_status(
            "Status.str.contains('(?i)failed')")
        self.delete_schedule_items_with_status(
            "Status.str.contains('(?i)completed/failures')")

        self.delete_duplicates_items_from_schedules()
        self.remove_schedule_olds()
        self.copy_schedule_link_to_table_schedule()
        self.separate_table_schedule_men_sem()
        self.delete_email_saved()

        print('Filters applied')

    def delete_email_saved(self):
        ScheduleOrLink.objects.filter(id=self.key_).delete()

    """ check if specification contains dia if true delete row """

    def check_query_and_apply_filter(self, query):
        [schedule_colum_exist, link_colum_exist] = self.colum_exist(query)

        """ Saved deleted rows for vcenter """
        table_schedule_deleted_days = self.table_schedule[0].query(
            query, engine='python') if schedule_colum_exist else None

        table_link_deleted_days = self.table_link[0].query(
            query, engine='python') if link_colum_exist else None

        """ write excel with deleted rows """
        if table_schedule_deleted_days is not None:
            self.write_excel_file(
                table_schedule_deleted_days, self.GET_ENV('FILE_2'))

        if table_link_deleted_days is not None:
            self.write_excel_file(table_link_deleted_days,
                                  self.GET_ENV('FILE_3'))

        """ Delete rows with dia in schedule or link """
        if schedule_colum_exist:
            self.table_schedule[0].drop(
                table_schedule_deleted_days.index, inplace=True)
            self.table_schedule[0].reset_index(drop=True, inplace=True)
        if link_colum_exist:
            self.table_link[0].drop(
                table_link_deleted_days.index, inplace=True)
            self.table_link[0].reset_index(drop=True, inplace=True)

    """ replace into colum values for new values """

    def replace_string_into_column(self, old, new, colum, limit=0):
        start_with = old.replace('(?i)', '')
        self.table_schedule[0][colum] = self.table_schedule[0][colum].map(lambda x: re.sub(
            old, new, x, limit) if x.lower().startswith(start_with) else x)

        self.table_schedule[0][colum] = self.table_schedule[0][colum].str.strip()

    """ Return if colum exist in table """

    def colum_exist(self, query):
        first_value_split = query.split('.')[0].replace("`", "")
        schedule_colum_exist = first_value_split in self.table_schedule[0].columns.values
        link_colum_exist = first_value_split in self.table_link[0].columns.values
        return [schedule_colum_exist, link_colum_exist]

    """ Delete items with status """

    def delete_schedule_items_with_status(self, query):
        table_only_filters = self.table_schedule[0].query(
            query, engine='python')

        self.write_excel_file(table_only_filters, self.GET_ENV('FILE_2'))

        self.table_schedule[0].drop(table_only_filters.index, inplace=True)

    """ Delete duplicate items in colum """

    def delete_duplicates_items_from_schedules(self):
        self.table_schedule[0].sort_values(
            by=['Start Time'], inplace=True)

        self.table_schedule[0].drop_duplicates(
            subset=['Specification'], keep='last', inplace=True)

        self.table_schedule[0].sort_values(by=['Specification'], inplace=True)

    """ Remove old schedule not contain in link """

    def remove_schedule_olds(self):
        self.table_schedule[0]['Specification_lower'] = self.table_schedule[0]['Specification'].str.lower()
        self.table_link[0]['Specification_lower'] = self.table_link[0]['Specification'].str.lower()

        table_schedule_olds = pd.merge(self.table_schedule[0], self.table_link[0],
                                       how='left', on=['Specification_lower'], indicator=True).set_axis(self.table_schedule[0].index)
        table_schedule_olds['_merge'] = table_schedule_olds['_merge'] == 'left_only'
        table_schedule_olds = table_schedule_olds.query(
            '_merge == True', engine='python')

        self.write_excel_file(table_schedule_olds, self.GET_ENV('FILE_2'))

        """ delete only table_schedule._merge == True """
        self.table_schedule[0].drop(table_schedule_olds.index, inplace=True)

    """ Copy schedule link to table schedule """

    def copy_schedule_link_to_table_schedule(self):
        table_schedule_copy = pd.merge(self.table_schedule[0], self.table_link[0], how='right', on=[
            'Specification_lower'], indicator=True).set_axis(self.table_link[0].index)
        table_schedule_copy['_merge'] = table_schedule_copy['_merge'] == 'right_only'

        table_schedule_copy = table_schedule_copy.query(
            '_merge == True', engine='python')

        self.table_schedule[0].drop(
            columns=['Specification_lower'], axis=1, inplace=True)
        self.table_link[0].drop(
            columns=['Specification_lower'], axis=1, inplace=True)

        table_schedule_copy = table_schedule_copy.drop(
            columns=['_merge', 'Specification_lower', 'Type'], axis=1)

        self.table_schedule[0] = pd.merge(
            self.table_schedule[0], table_schedule_copy, how='left')

    """ Separate schedule to week and month """

    def separate_table_schedule_men_sem(self):
        table_schedule_sem = self.table_schedule[0].query(
            "Specification.str.contains('(?i)sem')", engine='python')
        table_schedule_men = self.table_schedule[0].query(
            "Specification.str.contains('(?i)men')")

        self.table_schedule[0].drop(table_schedule_sem.index, inplace=True)
        self.table_schedule[0].drop(table_schedule_men.index, inplace=True)

        table_schedule_sem = table_schedule_sem.sort_values(
            by=['Specification'])
        table_schedule_men = table_schedule_men.sort_values(
            by=['Specification'])
        self.table_schedule[0].sort_values(by=['Specification'], inplace=True)

        self.write_excel_file(table_schedule_sem, self.GET_ENV('FILE_1'))
        self.write_excel_file(table_schedule_men, self.GET_ENV('FILE_4'))
        self.write_excel_file(self.table_schedule[0], self.GET_ENV('FILE_5'))

    """ Write excel file """

    def write_excel_file(self, table, file_name):
        wb = load_workbook(file_name)

        sheet_exist = self.key_ in wb.sheetnames

        writer = pd.ExcelWriter(file_name, engine='openpyxl')
        writer.book = wb

        """ Copy all sheets of file """
        writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)

        if sheet_exist:
            """ writer in sheet if exist"""
            book_writed = len(wb[self.key_]['A']) + 1

            table.to_excel(writer, sheet_name=self.key_,
                           startrow=book_writed, index=False, header=False)
        else:
            table.to_excel(writer, sheet_name=self.key_, index=False)

        writer.save()
        return writer.close()

    """ Delete sheet innecesary"""

    def deleteSheet(self, file_name, sheet_name):
        wb = load_workbook(file_name)
        del wb[sheet_name]
        wb.save(file_name)
        wb.close()

    def delete_files(self):
        file = [self.GET_ENV('FILE_1'), self.GET_ENV('FILE_2'), self.GET_ENV(
            'FILE_3'), self.GET_ENV('FILE_4'), self.GET_ENV('FILE_5')]
        for f in file:
            path = os.path.join(settings.BASE_DIR, f)
            os.remove(path)

        for f in file:
            MainProcessCollect.saveFirstFile(f)
