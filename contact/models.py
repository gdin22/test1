from django.db import models

# Create your models here.


class Contacts(models.Model):  # 导入的excel中的关键词
    key = models.CharField(max_length=32)


class SaveKeys(models.Model):  # 需要保存的关键词
    key = models.CharField(max_length=32)
