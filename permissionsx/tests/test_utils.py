"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.contrib.auth.models import User
from django.test import (
    TestCase,
    RequestFactory,
)
from django.test.client import Client
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import logout

from permissionsx.tests.models import Profile
from permissionsx.models import Permissions
from permissionsx import settings


DEFAULT_PASSWORD = 'password'


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
        user = User.objects.create_user(username, username + '@example.com', DEFAULT_PASSWORD)
        user.profile = Profile.objects.create(user=user)
        user.__dict__.update(**attrs)
        user.backend = self.session_backend
        user.save()
        return user

    def login(self, client, username):
        client.login(username=username, password=DEFAULT_PASSWORD)

    def get_request_for_user(self, user):
        request = self.factory.get('/')
        request.user = self.user
        self.session_middleware.process_request(request)
        logout(request)
        return request

    def permissions_for_request(self, permissions, request):
        if isinstance(permissions, Permissions):
            return permissions.check_permissions(request)
        else:
            return permissions().check_permissions(request)


# NOTE: SettingsOverride comes from `https://github.com/divio/django-cms/`.

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
