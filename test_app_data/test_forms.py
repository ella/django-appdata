from datetime import date

from django import forms
from django.forms.models import ModelChoiceField, modelform_factory

from app_data.forms import multiform_factory
from app_data.registry import app_registry
from app_data.containers import AppDataContainer, AppDataForm

from nose import tools

from .cases import AppDataTestCase
from .models import Article

class TestMultiForm(AppDataTestCase):
    class MyForm(AppDataForm):
        title = forms.CharField(max_length=100)
        publish_from = forms.DateField()
        publish_to = forms.DateField(required=False)
        related_article = ModelChoiceField(queryset=Article.objects.all(), required=False)

    def setUp(self):
        super(TestMultiForm, self).setUp()
        MyAppContainer = AppDataContainer.from_form(self.MyForm)
        app_registry.register('myapp', MyAppContainer)

    def test_multi_form_saves_all_the_forms(self):
        ModelForm = modelform_factory(Article)
        MF = multiform_factory(ModelForm, myapp={})
        data = {
            'myapp-title': 'First',
            'myapp-publish_from': '2010-11-12',
        }
        form = MF(data)
        tools.assert_true(form.is_valid())
        art = form.save()
        tools.assert_equals(
            {
                'myapp': {
                    'publish_from': '2010-11-12',
                    'publish_to': None,
                    'related_article': None,
                    'title': u'First'
                }
            },
            art.app_data
        )


class TestAppDataForms(AppDataTestCase):
    class MyForm(AppDataForm):
        title = forms.CharField(max_length=100)
        publish_from = forms.DateField()
        publish_to = forms.DateField(required=False)
        related_article = ModelChoiceField(queryset=Article.objects.all(), required=False)

    def setUp(self):
        super(TestAppDataForms, self).setUp()
        MyAppContainer = AppDataContainer.from_form(self.MyForm)
        app_registry.register('myapp', MyAppContainer)
        self.data = {
            'title': 'First!',
            'publish_from': '2010-10-1'
        }

    def test_foreign_keys_can_be_used(self):
        rel = Article.objects.create()
        self.data['related_article'] = str(rel.pk)

        article = Article()
        form = article.app_data.myapp.get_form(self.data)
        tools.assert_true(form.is_valid())
        form.save()
        article.save()
        article = Article.objects.get(pk=article.pk)
        tools.assert_equals(rel, article.app_data.myapp.related_article)

    def test_form_save_alters_data_on_model(self):
        article = Article()
        form = article.app_data.myapp.get_form(self.data)
        tools.assert_true(form.is_valid())
        form.save()
        article.save()
        article = Article.objects.get(pk=article.pk)
        tools.assert_equals(date(2010, 10, 1), article.app_data.myapp.publish_from)

    def test_form_with_limitted_fields_only_updates_those(self):
        article = Article()
        form = article.app_data.myapp.get_form(self.data, fields=['title',])
        tools.assert_true(form.is_valid())
        form.save()

        article.save()
        article = Article.objects.get(pk=article.pk)
        tools.assert_equals({u'title': u'First!'}, article.app_data.myapp._data)

