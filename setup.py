from os.path import join, dirname
from setuptools import setup


VERSION = (0, 1, 6)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

f = open(join(dirname(__file__), 'README.rst'))
long_description = f.read().strip()
f.close()

install_requires = [
    'Django>=1.4.10',
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
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=install_requires,

    test_suite='test_app_data.run_tests.run_all',
    tests_require=test_requires,
)
