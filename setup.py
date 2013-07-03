from os.path import join, dirname
from setuptools import setup


VERSION = (0, 1, 3)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

f = open(join(dirname(__file__), 'README.rst'))
long_description = f.read().strip()
f.close()

install_requires = [
    'Django',
    'south>=0.7',
]
test_requires = [
    'nose',
    'coverage',
]

setup(
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
    classifiers = [
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
    ],
    install_requires=install_requires,

    test_suite='test_app_data.run_tests.run_all',
    test_requires=test_requires,
)
