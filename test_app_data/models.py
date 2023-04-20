from django import forms
from django.db import models

from app_data import AppDataContainer, AppDataField, AppDataForm, NamespaceRegistry, app_registry


class Category(models.Model):
    app_data = AppDataField()


class Publishable(models.Model):
    app_data = AppDataField()


class Article(Publishable):
    file = models.FileField(blank=True)


class Author(models.Model):
    publishable = models.ForeignKey(Publishable, on_delete=models.CASCADE)
    app_data = AppDataField()


class AlternateRegistryModel(models.Model):
    alternate_registry = NamespaceRegistry()
    app_data = AppDataField(app_registry=alternate_registry)


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


class AlternateRegistryAppForm(AppDataForm):
    alternate_field = forms.CharField(max_length=20, required=False)


app_registry.register("publish", AppDataContainer.from_form(PublishAppForm))
app_registry.register("rss", AppDataContainer.from_form(RSSAppForm))
app_registry.register("personal", AppDataContainer.from_form(PersonalAppForm))
AlternateRegistryModel.alternate_registry.register("alternate", AppDataContainer.from_form(AlternateRegistryAppForm))
