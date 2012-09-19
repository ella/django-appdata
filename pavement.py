from paver.easy import path, options
from paver.setuputils import setup


VERSION = (0, 0, 1)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

f = (path(__file__).dirname() / 'README.rst').open()
long_description = f.read().strip()
f.close()

f = (path(__file__).dirname() / 'requirements.txt').open()
install_requires = f.read().strip()
f.close()


options(
    setup = dict(
    name = 'django-appdata',
    description = "Extandable field that enables Django apps to store their data on your models.",
    url = "https://github.com/ella/django-appdata/",
    long_description = long_description,
    version = __versionstr__,
    author = 'Ella Development Team',
    author_email = 'dev@ellaproject.cz',
    license='BSD',
    packages = ['app_data'],
    zip_safe = False,
    include_package_data = True,
    install_requires = install_requires,
    test_suite = 'test_app_data.run_tests.run_all',
    classifiers = [
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
    ]),
)

setup(**options.setup)

