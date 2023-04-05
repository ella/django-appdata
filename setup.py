from os.path import dirname, join

from setuptools import setup

VERSION = (0, 3, 2)
__version__ = VERSION
__versionstr__ = ".".join(map(str, VERSION))

f = open(join(dirname(__file__), "README.rst"))
long_description = f.read().strip()
f.close()

install_requires = ["Django", "six"]
test_requires = [
    "coverage",
]

setup(
    name="django-appdata",
    description="Extendable field that enables Django apps to store their data on your models.",
    url="https://github.com/ella/django-appdata/",
    long_description=long_description,
    version=__versionstr__,
    author="Ella Development Team",
    author_email="dev@ellaproject.cz",
    license="BSD",
    packages=["app_data"],
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    install_requires=install_requires,
    test_suite="test_app_data.runtests.run_tests",
    tests_require=test_requires,
)
