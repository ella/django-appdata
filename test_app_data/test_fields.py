import pickle
from datetime import date

from django import forms

from app_data.containers import AppDataContainer, AppDataForm
from app_data.registry import NamespaceConflict, NamespaceMissing, app_registry

from .cases import AppDataTestCase
from .models import AlternateRegistryModel, Article, Publishable


class DummyAppDataContainer(AppDataContainer):
    pass


class DummyAppDataContainer2(AppDataContainer):
    pass


class TestForms(AppDataTestCase):
    def test_container_from_form(self):
        class MyForm(AppDataForm):
            publish_from = forms.DateField()

        MyAppContainer = AppDataContainer.from_form(MyForm)  # noqa: N806
        app_registry.register("myapp", MyAppContainer)

        art = Article()
        self.assertTrue(isinstance(art.app_data["myapp"], MyAppContainer))

    def test_initial_get_used_as_default(self):
        class MyForm(AppDataForm):
            title = forms.CharField(max_length=25, initial="Hullo!")

        MyAppContainer = AppDataContainer.from_form(MyForm)  # noqa: N806
        app_registry.register("myapp", MyAppContainer)

        art = Article()
        self.assertTrue(isinstance(art.app_data["myapp"], MyAppContainer))
        self.assertEqual("Hullo!", art.app_data.myapp.get("title"))

    def test_get_fallback_value(self):
        class MyForm(AppDataForm):
            title = forms.CharField(max_length=25, initial="Hullo!")

        MyAppContainer = AppDataContainer.from_form(MyForm)  # noqa: N806
        app_registry.register("myapp", MyAppContainer)

        art = Article()
        self.assertEqual(None, art.app_data.myapp.get("foo"))
        self.assertEqual("bar", art.app_data.myapp.get("foo", "bar"))

    def test_get_semantics_for_getitem(self):
        class MyForm(AppDataForm):
            title = forms.CharField(max_length=25, initial="Hullo!")
            description = forms.CharField(max_length=25, required=False)

        MyAppContainer = AppDataContainer.from_form(MyForm)  # noqa: N806
        app_registry.register("myapp", MyAppContainer)

        art = Article()
        self.assertEqual("Hullo!", art.app_data.myapp.title)
        # empty initial value falls back to field's type
        self.assertEqual("", art.app_data.myapp.description)


class TestSerialization(AppDataTestCase):
    class MyForm(AppDataForm):
        publish_from = forms.DateField()

    def setUp(self):
        super().setUp()

        MyAppContainer = AppDataContainer.from_form(self.MyForm)  # noqa: N806
        app_registry.register("myapp", MyAppContainer)
        self.article = Article()
        self.article.app_data.myapp.publish_from = date(2012, 8, 26)
        self.article.save()

    def _test_article(self, art):
        self.assertEqual({"myapp": {"publish_from": "2012-08-26"}}, art.app_data)
        self.assertEqual({"publish_from": "2012-08-26"}, art.app_data.myapp._data)

        self.assertEqual(date(2012, 8, 26), art.app_data.myapp["publish_from"])
        self.assertEqual(date(2012, 8, 26), art.app_data.myapp.publish_from)

    def test_dates_are_serialized_on_write(self):
        art = Article.objects.get(pk=self.article.pk)
        self._test_article(art)

    def test_pickle_support(self):
        data = pickle.dumps(self.article)
        unpickled_article = pickle.loads(data)
        self._test_article(unpickled_article)

    def test_pickle_supports_containers(self):
        self.article.app_data.myapp
        data = pickle.dumps(self.article)
        unpickled_article = pickle.loads(data)
        self._test_article(unpickled_article)


class TestAppDataContainers(AppDataTestCase):
    def test_registered_classes_can_behave_as_attrs(self):
        app_registry.register("dummy", DummyAppDataContainer)
        art = Article()
        self.assertTrue(isinstance(art.app_data.dummy, DummyAppDataContainer))

    def test_registered_classes_can_be_set_as_attrs(self):
        app_registry.register("dummy", DummyAppDataContainer)
        art = Article()
        art.app_data.dummy = {"answer": 42}
        self.assertTrue(isinstance(art.app_data.dummy, DummyAppDataContainer))
        self.assertEqual(DummyAppDataContainer(art, {"answer": 42}), art.app_data.dummy)
        self.assertEqual({"dummy": {"answer": 42}}, art.app_data)

    def test_registered_classes_get_stored_on_access(self):
        app_registry.register("dummy", DummyAppDataContainer)
        art = Article()
        art.app_data["dummy"]
        self.assertEqual({"dummy": {}}, art.app_data)

    def test_namespace_can_only_be_registered_once(self):
        with self.assertRaises(NamespaceConflict):
            app_registry.register("dummy", DummyAppDataContainer)
            app_registry.register("dummy", DummyAppDataContainer2)

    def test_unregistered_namespace_cannot_be_unregistered(self):
        with self.assertRaises(NamespaceMissing):
            app_registry.register("dummy", DummyAppDataContainer)
            app_registry.unregister("dummy")
            app_registry.unregister("dummy")

    def test_override_class_for_model_only(self):
        app_registry.register("dummy", DummyAppDataContainer)
        app_registry.register("dummy", DummyAppDataContainer2, model=Publishable)
        inst = Publishable()
        self.assertTrue(isinstance(inst.app_data.get("dummy", {}), DummyAppDataContainer2))

    def test_get_app_data_returns_registered_class_instance(self):
        app_registry.register("dummy", DummyAppDataContainer)
        inst = Publishable()
        self.assertTrue(isinstance(inst.app_data.get("dummy", {}), DummyAppDataContainer))

    def test_existing_values_get_wrapped_in_proper_class(self):
        app_registry.register("dummy", DummyAppDataContainer)
        inst = Publishable()
        inst.app_data = {"dummy": {"hullo": "there"}}
        self.assertTrue(isinstance(inst.app_data["dummy"], DummyAppDataContainer))

    def test_get_app_data_returns_default_class_if_not_registered(self):
        app_registry.default_class = AppDataContainer
        inst = Publishable()
        self.assertTrue(isinstance(inst.app_data.get("dummy", {}), AppDataContainer))

    def test_app_data_container_behaves_like_dict(self):
        inst = Publishable()
        data = inst.app_data.get("dummy", {})
        data["foo"] = "bar"
        self.assertEqual(data["foo"], "bar")
        self.assertEqual(list(data.keys()), ["foo"])
        self.assertEqual(list(data.values()), ["bar"])

    def test_alternate_registry(self):
        def _get_namespace(instance, namespace):
            return getattr(instance, namespace)

        alt = AlternateRegistryModel()
        # only the "alternate" namespace should be in this model's registry
        self.assertEqual(alt.app_data.alternate.alternate_field, "")
        with self.assertRaises(AttributeError):
            _get_namespace(alt, "publish")
        # and the "alternate" namespace shouldn't be in the global registry
        inst = Publishable()
        with self.assertRaises(AttributeError):
            _get_namespace(inst, "alternate")
