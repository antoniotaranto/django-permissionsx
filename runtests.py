"""PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'permissionsx'))

import django
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
        'django.contrib.staticfiles',
        'debug_toolbar',
        'permissionsx.tests',
        'permissionsx',
    ],
    'STATIC_URL': '/static/',
    'AUTH_USER_MODEL': 'tests.Profile',
    'MIDDLEWARE_CLASSES': (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ),
    'DEBUG': False,
    'SHOW_TOOLBAR': False,
    'DEBUG_TOOLBAR_PANELS': (
        'permissionsx.contrib.django_debug_toolbar.PermissionsPanel',
    ),
    'DEBUG_TOOLBAR_CONFIG': {
        'INTERCEPT_REDIRECTS': False,
        'SHOW_TOOLBAR_CALLBACK': 'permissionsx.tests.utils.show_toolbar',
    },
    'TEMPLATE_DIRS': (
        os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates'),
        os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tests/templates'),
    ),
    'ROOT_URLCONF': 'permissionsx.tests.urls',
}

settings.configure(**configure_settings)

from django.test.utils import get_runner
if django.VERSION >= (1, 7):
    django.setup()

test_runner = get_runner(settings)
failures = test_runner(
    verbosity=1,
    interactive=False,
    failfast=False).run_tests(['tests'])
sys.exit(failures)
