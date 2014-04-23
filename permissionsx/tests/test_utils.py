"""PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

from django.test import (
    RequestFactory,
    TestCase,
)
from django.contrib.auth import (
    get_user_model,
    logout,
)
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import Client

from permissionsx import settings
from permissionsx.tests.models import Profile


DEFAULT_PASSWORD = 'password'


def show_toolbar(request):
    return True


class UtilityTestCase(TestCase):

    def setUp(self):
        self.session_backend = SessionStore()
        self.session_middleware = SessionMiddleware()
        self.factory = RequestFactory()
        self.user = self.create_user('user')
        self.admin = self.create_user('admin', is_superuser=True)
        self.staff = self.create_user('staff', is_staff=True)
        self.client = Client()

    def create_user(self, username, **attrs):
        if attrs is None:
            attrs = {}
        user = get_user_model().objects.create_user(
            username,
            username + '@example.com',
            DEFAULT_PASSWORD
        )
        for name, value in attrs.items():
            setattr(user, name, value)
        user.backend = self.session_backend
        user.save()
        return user

    def login(self, client, username):
        client.login(username=username, password=DEFAULT_PASSWORD)

    def get_request_for_user(self, user, url=None):
        if url is None:
            url = '/'
        request = self.factory.get(url)
        request.user = self.user
        self.session_middleware.process_request(request)
        logout(request)
        return request


# NOTE: SettingsOverride comes from `https://github.com/divio/django-cms/`.
#       For a reason I can't already remember decorator and context manager
#       provided by Django don't work with tests.
class NULL:
    pass


class SettingsOverride(object):

    def __init__(self, **overrides):
        self.overrides = overrides

    def __enter__(self):
        self.old = {}
        for key, value in self.overrides.items():
            self.old[key] = getattr(settings, key, NULL)
            setattr(settings, key, value)

    def __exit__(self, type, value, traceback):
        for key, value in self.old.items():
            if value is not NULL:
                setattr(settings, key, value)
            else:
                delattr(settings, key)
