#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


def run_tests():
    os.environ["DJANGO_SETTINGS_MODULE"] = "test_app_data.settings"
    django.setup()
    TestRunner = get_runner(settings)  # noqa: N806
    test_runner = TestRunner()
    failures = test_runner.run_tests(["test_app_data"])
    sys.exit(bool(failures))
