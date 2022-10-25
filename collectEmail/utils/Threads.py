
from functools import lru_cache
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from collectEmail.utils.MainProcess import MainProcessCollect
from django.utils import timezone
import environ


class ThreadsStart():

    GET_ENV = environ.Env()

    def __init__(self):
        self.readEmailThread()

    def readEmailThread(self):
        MainProcessCollect.saveFirstFile(self.GET_ENV('FILE_1'))
        MainProcessCollect.saveFirstFile(self.GET_ENV('FILE_2'))
        MainProcessCollect.saveFirstFile(self.GET_ENV('FILE_3'))
        MainProcessCollect.saveFirstFile(self.GET_ENV('FILE_4'))
        MainProcessCollect.saveFirstFile(self.GET_ENV('FILE_5'))

        scheduler = BackgroundScheduler()
        scheduler.add_job(MainProcessCollect, 'interval',
                          seconds=60*20, next_run_time=timezone.now(), id='collect_data_from_email', replace_existing=True)
        scheduler.start()
