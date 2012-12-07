from django import forms
from django.db import models

from app_data import AppDataField, AppDataContainer, AppDataForm, app_registry

class Category(models.Model):
    app_data = AppDataField()

class Publishable(models.Model):
    app_data = AppDataField()

class Article(Publishable):
    pass

class Author(models.Model):
    publishable = models.ForeignKey(Publishable)
    app_data = AppDataField()

class PublishAppForm(AppDataForm):
    publish_from = forms.DateTimeField()
    published = forms.BooleanField(required=False)
    publish_to = forms.DateTimeField(required=False)

class RSSAppForm(AppDataForm):
    title = forms.CharField(max_length=20)
    author = forms.CharField(max_length=20)
    description = forms.CharField(max_length=200)

class PersonalAppForm(AppDataForm):
    first_name = forms.CharField(max_length=20, required=False)
    last_name = forms.CharField(max_length=20, required=False)

app_registry.register('publish', AppDataContainer.from_form(PublishAppForm))
app_registry.register('rss', AppDataContainer.from_form(RSSAppForm))
app_registry.register('personal', AppDataContainer.from_form(PersonalAppForm))
