
from functools import lru_cache
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from collectEmail.utils.MainProcess import MainProcessCollect
from django.utils import timezone


class ThreadsStart():

    def __init__(self):
        self.readEmailThread()

    def readEmailThread(self):
        MainProcessCollect.saveFirstFile()

        scheduler = BackgroundScheduler()
        scheduler.add_job(MainProcessCollect, 'interval',
                          seconds=60*5, next_run_time=timezone.now(), id='collect_data_from_email', replace_existing=True)
        scheduler.start()
