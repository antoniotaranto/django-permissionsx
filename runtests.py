"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'permissionsx'))

from django.conf import settings

configure_settings = {
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    'SECRET_KEY': 'THIS_IS_SECRET',
    'INSTALLED_APPS': [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'permissionsx.tests',
        'permissionsx',
    ],
    'AUTH_PROFILE_MODULE': 'tests.Profile',
    'MIDDLEWARE_CLASSES': (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ),
    'TEMPLATE_DIRS': (
        os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates'),
        os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tests/templates'),
    ),
    'ROOT_URLCONF': 'permissionsx.tests.test_urls',
}

settings.configure(**configure_settings)

from django.test.utils import get_runner
test_runner = get_runner(settings)
failures = test_runner(verbosity=1, interactive=False, failfast=False).run_tests(['tests'])
sys.exit(failures)
