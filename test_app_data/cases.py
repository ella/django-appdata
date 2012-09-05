from django.test import TestCase
from django.conf import settings

from app_data.registry import app_registry

class AppDataTestCase(TestCase):
    def tearDown(self):
        super(AppDataTestCase, self).tearDown()
        if hasattr(settings, 'APP_DATA_CLASSES'):
            del settings.APP_DATA_CLASSES
        app_registry._reset()
        app_registry.default_class = None

