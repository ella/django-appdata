from django.db import models

from app_data import AppDataField

class Category(models.Model):
    app_data = AppDataField()

class Publishable(models.Model):
    app_data = AppDataField()

class Article(Publishable):
    pass

