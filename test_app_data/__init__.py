from os import environ

import django

environ["DJANGO_SETTINGS_MODULE"] = "test_app_data.settings"

test_runner = None
old_config = None

django.setup()


def setup():
    from django.test.runner import DiscoverRunner

    global test_runner
    global old_config

    test_runner = DiscoverRunner()

    test_runner.setup_test_environment()
    old_config = test_runner.setup_databases()


def teardown():
    test_runner.teardown_databases(old_config)
    test_runner.teardown_test_environment()
