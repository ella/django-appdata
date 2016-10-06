test_runner = None
old_config = None

def setup():
    global test_runner
    global old_config
    try:
        # Django 1.7
        from django.test.runner import DiscoverRunner
        import django
        django.setup()
        test_runner = DiscoverRunner()
    except (ImportError, AttributeError):
        from django.test.simple import DjangoTestSuiteRunner
        test_runner = DjangoTestSuiteRunner()

    test_runner.setup_test_environment()
    old_config = test_runner.setup_databases()

def teardown():
    test_runner.teardown_databases(old_config)
    test_runner.teardown_test_environment()


