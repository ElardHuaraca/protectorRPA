from time import localtime
from django.db import models

# Create your models here.


class Email(models.Model):
    email = models.CharField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)


class UltimateVerification(models.Model):
    comprovate = models.DateTimeField(auto_now_add=True)
