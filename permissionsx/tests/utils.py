"""PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

from django.conf import settings as django_settings
from django.test import (
    RequestFactory,
    TestCase,
)
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import Client


DEFAULT_PASSWORD = 'password'


def show_toolbar(request):
    return django_settings.SHOW_TOOLBAR


class UtilityTestCase(TestCase):

    def setUp(self):
        self.session_backend = SessionStore()
        self.session_middleware = SessionMiddleware()
        self.factory = RequestFactory()
        self.user = self.create_user('user')
        self.owner = self.create_user('owner')
        self.admin = self.create_user('admin', is_superuser=True)
        self.staff = self.create_user('staff', is_staff=True)
        self.client = Client()

    def create_user(self, username, **attrs):
        user = get_user_model().objects.create_user(
            username,
            username + '@example.com',
            DEFAULT_PASSWORD
        )
        for name, value in attrs.items():
            setattr(user, name, value)
        user.save()
        return user

    def login(self, client, username):
        client.login(username=username, password=DEFAULT_PASSWORD)

    def get_request(self, url=None):
        if url is None:
            url = '/'
        request = self.factory.get(url)
        request.user = AnonymousUser()
        self.session_middleware.process_request(request)
        return request
