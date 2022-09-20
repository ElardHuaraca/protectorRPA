from sched import scheduler
from django.apps import AppConfig
from threading import Thread
from time import sleep
from .utils.MainProcess import MainProcessCollect
from apscheduler.schedulers.background import BackgroundScheduler


class ReadEmailThread():
    scheduler = BackgroundScheduler()
    if not scheduler.get_job('collect_data_from_email'):
        scheduler.add_job(MainProcessCollect, 'interval',
                          seconds=5, id='collect_data_from_email')
        scheduler.start()


class CollectemailConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'collectEmail'

    def run(self):
        ReadEmailThread()
