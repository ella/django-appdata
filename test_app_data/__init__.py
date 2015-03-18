import django

test_runner = None
old_config = None

def setup():
    global test_runner
    global old_config
    try:
        # Django 1.6 and higher
        from django.test.runner import DiscoverRunner as TestRunner
    except ImportError:
        from django.test.simple import DjangoTestSuiteRunner as TestRunner
    try:
        # Django 1.7 and higher
        django.setup()
    except AttributeError:
        pass

    test_runner = TestRunner()
    test_runner.setup_test_environment()
    old_config = test_runner.setup_databases()

def teardown():
    test_runner.teardown_databases(old_config)
    test_runner.teardown_test_environment()


