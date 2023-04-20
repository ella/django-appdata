from datetime import date

from django import forms
from django.forms.models import ModelChoiceField, modelform_factory

from app_data.containers import AppDataContainer, AppDataForm
from app_data.fields import ListModelMultipleChoiceField
from app_data.forms import MultiForm, multiform_factory, multiformset_factory
from app_data.registry import app_registry

from .cases import AppDataTestCase
from .models import Article, Category


class TestMultiForm(AppDataTestCase):
    class MyMultiForm(MultiForm):
        pass

    class MyForm(AppDataForm):
        title = forms.CharField(max_length=100)
        publish_from = forms.DateField()
        publish_to = forms.DateField(required=False)
        related_article = ModelChoiceField(
            queryset=Article.objects.all(),
            required=False,
        )

    class MyForm2(AppDataForm):
        foo = forms.CharField(max_length=100)

    def setUp(self):
        super().setUp()
        MyAppContainer = AppDataContainer.from_form(self.MyForm)  # noqa: N806
        app_registry.register("myapp", MyAppContainer)
        app_registry.register("myapp2", AppDataContainer.from_form(self.MyForm2))

    def test_multi_form_can_work_with_formsets(self):
        FormSet = multiformset_factory(Article, form_opts={"myapp": {}}, exclude=())  # noqa: N806
        data = {
            "fs-TOTAL_FORMS": "1",
            "fs-INITIAL_FORMS": "0",
            "fs-0-myapp-title": "First",
            "fs-0-myapp-publish_from": "2010-11-12",
        }
        formset = FormSet(data, prefix="fs")

        self.assertTrue(formset.is_valid())
        formset.save()
        self.assertEqual(1, Article.objects.count())
        art = Article.objects.all()[0]
        self.assertEqual(
            {
                "myapp": {
                    "publish_from": "2010-11-12",
                    "publish_to": None,
                    "related_article": None,
                    "title": "First",
                },
            },
            art.app_data,
        )

    def test_multi_form_saves_all_the_forms(self):
        MF = multiform_factory(Article, form_opts={"myapp": {}, "myapp2": {}}, exclude=())  # noqa: N806
        data = {
            "myapp-title": "First",
            "myapp-publish_from": "2010-11-12",
            "myapp2-foo": "Second",
        }
        form = MF(data)
        self.assertTrue(form.is_valid())
        self.assertEqual({}, form.errors)
        art = form.save()
        self.assertEqual(
            {
                "myapp": {
                    "publish_from": "2010-11-12",
                    "publish_to": None,
                    "related_article": None,
                    "title": "First",
                },
                "myapp2": {"foo": "Second"},
            },
            art.app_data,
        )

    def test_form_can_be_added_to_parent(self):
        MF = multiform_factory(Article, multiform=self.MyMultiForm, exclude=())  # noqa: N806
        self.MyMultiForm.add_form("myapp", {})
        data = {
            "myapp-title": "First",
            "myapp-publish_from": "2010-11-12",
        }
        form = MF(data)
        self.assertTrue(form.is_valid())
        self.assertEqual({}, form.errors)
        art = form.save()
        self.assertEqual(
            {
                "myapp": {
                    "publish_from": "2010-11-12",
                    "publish_to": None,
                    "related_article": None,
                    "title": "First",
                },
            },
            art.app_data,
        )

    def test_form_can_be_added(self):
        MF = multiform_factory(Article, exclude=())  # noqa: N806
        MF.add_form("myapp", {})
        data = {
            "myapp-title": "First",
            "myapp-publish_from": "2010-11-12",
        }
        form = MF(data)
        self.assertTrue(form.is_valid())
        self.assertEqual({}, form.errors)
        art = form.save()
        self.assertEqual(
            {
                "myapp": {
                    "publish_from": "2010-11-12",
                    "publish_to": None,
                    "related_article": None,
                    "title": "First",
                },
            },
            art.app_data,
        )

    def test_added_form_doesnt_appear_on_parent(self):
        ArticleModelForm = modelform_factory(Article, exclude=())  # noqa: N806

        class MF(MultiForm):
            ModelForm = ArticleModelForm

        MF.add_form("myapp", {})

        self.assertEqual({}, MultiForm.app_form_opts)

    def test_form_can_be_removed(self):
        MF = multiform_factory(Article, form_opts={"myapp": {}}, exclude=())  # noqa: N806
        MF.remove_form("myapp")
        data = {
            "myapp-title": "First",
            "myapp-publish_from": "2010-11-12",
        }
        form = MF(data)
        self.assertTrue(form.is_valid())
        self.assertEqual({}, form.errors)
        art = form.save()
        self.assertEqual({}, art.app_data)


class TestAppDataForms(AppDataTestCase):
    class MyForm(AppDataForm):
        title = forms.CharField(max_length=100)
        publish_from = forms.DateField()
        publish_to = forms.DateField(required=False)
        related_article = ModelChoiceField(queryset=Article.objects.all(), required=False)

    class MyOtherForm(AppDataForm):
        categories = ListModelMultipleChoiceField(Category.objects.all(), required=False)

    def setUp(self):
        super().setUp()
        MyAppContainer = AppDataContainer.from_form(self.MyForm)  # noqa: N806
        app_registry.register("myapp", MyAppContainer)
        self.data = {"title": "First!", "publish_from": "2010-10-1"}
        MyOtherContainer = AppDataContainer.from_form(self.MyOtherForm)  # noqa: N806
        app_registry.register("myotherapp", MyOtherContainer)

    def test_empty_list_model_multiple_choice_field(self):
        article = Article()
        self.assertTrue(isinstance(article.app_data.myotherapp.categories, list))
        self.assertEqual([], article.app_data.myotherapp.categories)

    def test_list_model_multiple_choice_field(self):
        c1, c2 = Category.objects.create(), Category.objects.create()

        article = Article()
        data = {"categories": [str(c1.pk), str(c2.pk)]}
        form = article.app_data.myotherapp.get_form(data)
        self.assertTrue(form.is_valid())
        form.save()
        article.save()
        article = Article.objects.get(pk=article.pk)
        self.assertTrue(isinstance(article.app_data.myotherapp.categories, list))
        self.assertEqual([c1, c2], article.app_data.myotherapp.categories)

    def test_instance_is_accessible_to_the_form(self):
        art = Article()
        form = art.app_data.myapp.get_form(self.data)

        self.assertTrue(art is form.instance)

    def test_foreign_keys_can_be_used(self):
        rel = Article.objects.create()
        self.data["related_article"] = str(rel.pk)

        article = Article()
        form = article.app_data.myapp.get_form(self.data)
        self.assertTrue(form.is_valid())
        form.save()
        article.save()
        article = Article.objects.get(pk=article.pk)
        self.assertEqual(rel, article.app_data.myapp.related_article)

    def test_current_app_data_will_be_used_as_initial(self):
        article = Article()
        article.app_data = {"myapp": {"title": "Hello", "publish_from": "2012-10-10"}}
        form = article.app_data.myapp.get_form()
        self.assertEqual({"title": "Hello", "publish_from": "2012-10-10"}, form.initial)

    def test_form_save_alters_data_on_model(self):
        article = Article()
        form = article.app_data.myapp.get_form(self.data)
        self.assertTrue(form.is_valid())
        form.save()
        article.save()
        article = Article.objects.get(pk=article.pk)
        self.assertEqual(date(2010, 10, 1), article.app_data.myapp.publish_from)

    def test_form_with_limitted_fields_only_updates_those(self):
        article = Article()
        form = article.app_data.myapp.get_form(
            self.data,
            fields=[
                "title",
            ],
        )
        self.assertTrue(form.is_valid())
        form.save()

        article.save()
        article = Article.objects.get(pk=article.pk)
        self.assertEqual("First!", article.app_data.myapp._data["title"])
        self.assertFalse("publish_from" in article.app_data.myapp._data)
