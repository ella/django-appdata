from paver.easy import path, options
from paver.setuputils import setup

VERSION = (0, 0, 1)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

f = (path(__file__).dirname() / 'README.rst').open()
long_description = f.read().strip()
f.close()


options(
    setup = dict(
    name = 'app_data',
    description = "app_data",
    url = "https://github.com/WhiskeyMedia/app_data/",
    long_description = long_description,
    version = __versionstr__,
    author = "Whiskey Media",
    author_email = "monitoring@whiskeymedia.com",
    packages = ['app_data'],
    zip_safe = False,
    include_package_data = True,
    test_suite = 'test_app_data.run_tests.run_all',
    classifiers = [
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
    ]),
)

setup(**options.setup)
