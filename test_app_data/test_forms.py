from datetime import date

from django import forms

from app_data.registry import app_registry
from app_data.containers import AppDataContainer, AppDataForm

from nose import tools

from .cases import AppDataTestCase
from .models import Article

class TestAppDataForms(AppDataTestCase):
    class MyForm(AppDataForm):
        title = forms.CharField(max_length=100)
        publish_from = forms.DateField()
        publish_to = forms.DateField(required=False)

    def setUp(self):
        super(TestAppDataForms, self).setUp()
        MyAppContainer = AppDataContainer.from_form(self.MyForm)
        app_registry.register('myapp', MyAppContainer)

    def test_form_save_alters_data_on_model(self):
        article = Article()
        data = {
            'title': 'First!',
            'publish_from': date(2010, 10, 1)
        }
        form = article.app_data.myapp.get_form(data)
        tools.assert_true(form.is_valid())
        form.save()
        article.save()
        article = Article.objects.get(pk=article.pk)
        tools.assert_equals(date(2010, 10, 1), article.app_data.myapp.publish_from)

    def test_form_with_limitted_fields_only_updates_those(self):
        article = Article()
        data = {
            'title': 'First!',
        }
        form = article.app_data.myapp.get_form(data, fields=['title',])
        tools.assert_true(form.is_valid())
        form.save()

        article.save()
        article = Article.objects.get(pk=article.pk)
        tools.assert_equals({u'title': u'First!'}, article.app_data.myapp._data)

