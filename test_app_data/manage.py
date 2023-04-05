#!/usr/bin/env python

import os
import sys
from os.path import abspath, dirname, join, pardir, split

from django.core.management import execute_from_command_line

# fix PYTHONPATH and DJANGO_SETTINGS for us
# django settings module
DJANGO_SETTINGS_MODULE = "{}.{}".format(split(abspath(dirname(__file__)))[1], "settings")
# pythonpath dirs
PYTHONPATH = [
    abspath(join(dirname(__file__), pardir, pardir)),
    abspath(join(dirname(__file__), pardir)),
]

# inject few paths to pythonpath
for p in PYTHONPATH:
    if p not in sys.path:
        sys.path.insert(0, p)

# django needs this env variable
os.environ["DJANGO_SETTINGS_MODULE"] = DJANGO_SETTINGS_MODULE


if __name__ == "__main__":
    execute_from_command_line()
