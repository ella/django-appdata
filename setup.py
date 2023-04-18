from setuptools import find_packages, setup

from app_data import __version__

install_requires = ["Django", "six"]
test_requires = [
    "coverage",
]

setup(
    name="django-appdata",
    description="Extendable field that enables Django apps to store their data on your models.",
    url="https://github.com/ella/django-appdata/",
    long_description=open("README.rst").read(),
    version=__version__,
    author="Ella Development Team",
    author_email="dev@ellaproject.cz",
    license="BSD",
    packages=find_packages(exclude=["test_app_data"]),
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
