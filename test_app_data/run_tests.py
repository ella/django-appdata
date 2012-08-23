#!/usr/bin/env python
import sys
from os import path, environ

import nose

environ['DJANGO_SETTINGS_MODULE'] = 'test_app_data.settings'


def run_all(argv=None):
    sys.exitfunc = lambda msg='Process shutting down...': sys.stderr.write(msg + '\n')
    if argv is None:
        argv = [
            'nosetests',
            '--with-coverage', '--cover-package=app_data', '--cover-erase',
            '--nocapture', '--nologcapture',
            '--verbose', '--no-skip'
        ]
    else:
        for p in ('--with-coverage', '--cover-package=app_data', '--cover-erase'):
            if p not in argv:
                argv.append(p)

    nose.run_exit(
        argv=argv,
        defaultTest=path.abspath(path.dirname(__file__))
    )

if __name__ == '__main__':
    run_all(sys.argv)

