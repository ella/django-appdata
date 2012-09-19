from datetime import date

from django import forms
from django.conf import settings
from django.forms.models import ModelChoiceField, modelform_factory

from app_data.forms import multiform_factory, MultiForm
from app_data.registry import app_registry
from app_data.containers import AppDataContainer, AppDataForm

from nose import tools

from .cases import AppDataTestCase
from .models import Article

class TestMultiForm(AppDataTestCase):
    class MyMultiForm(MultiForm):
        pass

    class MyForm(AppDataForm):
        title = forms.CharField(max_length=100)
        publish_from = forms.DateField()
        publish_to = forms.DateField(required=False)
        related_article = ModelChoiceField(queryset=Article.objects.all(), required=False)

    class MyForm2(AppDataForm):
        foo = forms.CharField(max_length=100)

    def setUp(self):
        super(TestMultiForm, self).setUp()
        MyAppContainer = AppDataContainer.from_form(self.MyForm)
        app_registry.register('myapp', MyAppContainer)
        app_registry.register('myapp2', AppDataContainer.from_form(self.MyForm2))

    def test_multi_form_saves_all_the_forms(self):
        ModelForm = modelform_factory(Article)
        MF = multiform_factory(ModelForm)
        MF.add_form('myapp')
        MF.add_form('myapp2')
        data = {
            'myapp-title': 'First',
            'myapp-publish_from': '2010-11-12',
            'myapp2-foo': 'Second',
        }
        form = MF(data)
        tools.assert_true(form.is_valid())
        tools.assert_equals({}, form.errors)
        art = form.save()
        tools.assert_equals(
            {
                'myapp': {
                    'publish_from': '2010-11-12',
                    'publish_to': None,
                    'related_article': None,
                    'title': u'First'
                },
                'myapp2': {'foo': 'Second'}
            },
            art.app_data
        )

    def test_form_can_be_added_to_parent(self):
        ModelForm = modelform_factory(Article)
        MF = multiform_factory(ModelForm, base_class=self.MyMultiForm)
        self.MyMultiForm.add_form('myapp', {})
        data = {
            'myapp-title': 'First',
            'myapp-publish_from': '2010-11-12',
        }
        form = MF(data)
        tools.assert_true(form.is_valid())
        tools.assert_equals({}, form.errors)
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

    def test_form_can_be_added(self):
        ModelForm = modelform_factory(Article)
        MF = multiform_factory(ModelForm)
        MF.add_form('myapp', {})
        data = {
            'myapp-title': 'First',
            'myapp-publish_from': '2010-11-12',
        }
        form = MF(data)
        tools.assert_true(form.is_valid())
        tools.assert_equals({}, form.errors)
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

    def test_form_can_be_removed(self):
        ModelForm = modelform_factory(Article)
        MF = multiform_factory(ModelForm, myapp={})
        MF.remove_form('myapp')
        data = {
            'myapp-title': 'First',
            'myapp-publish_from': '2010-11-12',
        }
        form = MF(data)
        tools.assert_true(form.is_valid())
        tools.assert_equals({}, form.errors)
        art = form.save()
        tools.assert_equals({}, art.app_data)

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

    def test_instance_is_accessible_to_the_form(self):
        art = Article()
        form = art.app_data.myapp.get_form(self.data)

        tools.assert_true(art is form.instance)

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

    def test_current_app_data_will_be_used_as_initial(self):
        article = Article()
        article.app_data = {'myapp': {'title': 'Hello', 'publish_from': '2012-10-10'}}
        form = article.app_data.myapp.get_form()
        tools.assert_equals({'title': 'Hello', 'publish_from': '2012-10-10'}, form.initial)

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

