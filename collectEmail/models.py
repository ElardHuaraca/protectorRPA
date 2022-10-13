from email.policy import default
from time import localtime
from django.db import models

# Create your models here.


class Email(models.Model):
    email = models.CharField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)


class UltimateVerification(models.Model):
    comprovate = models.DateTimeField(auto_now_add=True)


class ScheduleOrLink(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    body = models.CharField(max_length=255)
    type = models.CharField(max_length=255, default='schedule')
