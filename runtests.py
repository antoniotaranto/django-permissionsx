#!/usr/bin/env python
import os
import sys

from django.conf import settings

sys.path.append(os.path.join(os.path.dirname(__file__), 'permissionsx'))

settings.configure(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    SECRET_KEY='THIS_IS_SECRET',
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'tests',
    ],
    ROOT_URLCONF='tests.urls'
)

from django.test.utils import get_runner


TestRunner = get_runner(settings)
test_runner = TestRunner(verbosity=1, interactive=False, failfast=False)
failures = test_runner.run_tests(['tests'])
sys.exit(failures)