from django.conf import settings
from django.test import TestCase

from app_data.registry import app_registry


class AppDataTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self._old_global_registry = app_registry._global_registry.copy()
        self._old_model_registry = app_registry._model_registry.copy()

    def tearDown(self):
        super().tearDown()
        if hasattr(settings, "APP_DATA_CLASSES"):
            del settings.APP_DATA_CLASSES
        app_registry.default_class = None
        app_registry._global_registry = self._old_global_registry
        app_registry._model_registry = self._old_model_registry
