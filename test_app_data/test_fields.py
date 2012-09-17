from datetime import date

from django import forms

from nose import tools

from app_data.registry import NamespaceConflict, NamespaceMissing, app_registry
from app_data.containers import AppDataContainer, AppDataForm

from .models import Article, Publishable
from .cases import AppDataTestCase

class DummyAppDataContainer(AppDataContainer):
    pass

class DummyAppDataContainer2(AppDataContainer):
    pass

class TestForms(AppDataTestCase):
    def test_container_from_form(self):
        class MyForm(AppDataForm):
            publish_from = forms.DateField()
        MyAppContainer = AppDataContainer.from_form(MyForm)
        app_registry.register('myapp', MyAppContainer)

        art = Article()
        tools.assert_true(isinstance(art.app_data['myapp'], MyAppContainer))

    def test_initial_get_used_as_default(self):
        class MyForm(AppDataForm):
            title = forms.CharField(max_length=25, initial='Hullo!')
        MyAppContainer = AppDataContainer.from_form(MyForm)
        app_registry.register('myapp', MyAppContainer)

        art = Article()
        tools.assert_true(isinstance(art.app_data['myapp'], MyAppContainer))
        tools.assert_equals('Hullo!', art.app_data.myapp.get('title'))

    def test_get_semantics_for_getitem(self):
        class MyForm(AppDataForm):
            title = forms.CharField(max_length=25, initial='Hullo!')
            description = forms.CharField(max_length=25)
        MyAppContainer = AppDataContainer.from_form(MyForm)
        app_registry.register('myapp', MyAppContainer)

        art = Article()
        tools.assert_equals('Hullo!', art.app_data.myapp.title)
        # empty initial values default to None
        tools.assert_equals(None, art.app_data.myapp.description)


class TestSerialization(AppDataTestCase):
    def test_dates_are_serialized_on_write(self):
        class MyForm(AppDataForm):
            publish_from = forms.DateField()
        MyAppContainer = AppDataContainer.from_form(MyForm)
        app_registry.register('myapp', MyAppContainer)

        art = Article()
        my_app_data = art.app_data['myapp']
        my_app_data.publish_from = date(2012, 8, 26)
        art.save()

        art = Article.objects.get(pk=art.pk)
        tools.assert_equals({'myapp': {'publish_from': '2012-08-26'}}, art.app_data)
        tools.assert_equals({'publish_from': '2012-08-26'}, art.app_data.myapp._data)

        tools.assert_equals(date(2012, 8, 26), art.app_data.myapp['publish_from'])
        tools.assert_equals(date(2012, 8, 26), art.app_data.myapp.publish_from)

class TestAppDataContainers(AppDataTestCase):
    def test_registered_classes_can_behave_as_attrs(self):
        app_registry.register('dummy', DummyAppDataContainer)
        art = Article()
        tools.assert_true(isinstance(art.app_data.dummy, DummyAppDataContainer))

    def test_registered_classes_can_be_set_as_attrs(self):
        app_registry.register('dummy', DummyAppDataContainer)
        art = Article()
        art.app_data.dummy = {'answer': 42}
        tools.assert_true(isinstance(art.app_data.dummy, DummyAppDataContainer))
        tools.assert_equals(DummyAppDataContainer(art, {'answer': 42}), art.app_data.dummy)
        tools.assert_equals({'dummy': {'answer': 42}}, art.app_data)

    def test_registered_classes_get_stored_on_access(self):
        app_registry.register('dummy', DummyAppDataContainer)
        art = Article()
        art.app_data['dummy']
        tools.assert_equals({'dummy': {}}, art.app_data)

    @tools.raises(NamespaceConflict)
    def test_namespace_can_only_be_registered_once(self):
        app_registry.register('dummy', DummyAppDataContainer)
        app_registry.register('dummy', DummyAppDataContainer2)

    @tools.raises(NamespaceMissing)
    def test_unregistered_namespace_cannot_be_unregistered(self):
        app_registry.register('dummy', DummyAppDataContainer)
        app_registry.unregister('dummy')
        app_registry.unregister('dummy')

    def test_override_class_for_model_only(self):
        app_registry.register('dummy', DummyAppDataContainer)
        app_registry.register('dummy', DummyAppDataContainer2, model=Publishable)
        inst = Publishable()
        tools.assert_true(isinstance(inst.app_data.get('dummy', {}), DummyAppDataContainer2))

    def test_get_app_data_returns_registered_class_instance(self):
        app_registry.register('dummy', DummyAppDataContainer)
        inst = Publishable()
        tools.assert_true(isinstance(inst.app_data.get('dummy', {}), DummyAppDataContainer))

    def test_existing_values_get_wrapped_in_proper_class(self):
        app_registry.register('dummy', DummyAppDataContainer)
        inst = Publishable()
        inst.app_data = {'dummy': {'hullo': 'there'}}
        tools.assert_true(isinstance(inst.app_data['dummy'], DummyAppDataContainer))

    def test_get_app_data_returns_default_class_if_not_registered(self):
        app_registry.default_class = AppDataContainer
        inst = Publishable()
        tools.assert_true(isinstance(inst.app_data.get('dummy', {}), AppDataContainer))

    def test_app_data_container_behaves_like_dict(self):
        inst = Publishable()
        data = inst.app_data.get('dummy', {})
        data['foo'] = 'bar'
        tools.assert_equals(data['foo'], 'bar')
        tools.assert_equals(data.keys(), ['foo'])
        tools.assert_equals(data.values(), ['bar'])
