from django.db import models

# Create your models here.


class Contacts(models.Model):
    key = models.CharField(max_length=32)


class SaveKeys(models.Model):
    key = models.CharField(max_length=32)
