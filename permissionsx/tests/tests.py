"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""

from django.contrib.auth import (
    login,
    logout,
)
from django.contrib.auth.models import User
from django.test import (
    TestCase,
    RequestFactory,
)
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.middleware import SessionMiddleware

from permissionsx.tests.permissions import *
from permissionsx.tests.models import Profile


class PermissionsDefinitionsTests(TestCase):

    def setUp(self):
        self.session_backend = SessionStore()
        self.session_middleware = SessionMiddleware()
        self.factory = RequestFactory()
        self.user = self.create_user('user')
        self.admin = self.create_user('admin', is_superuser=True)
        self.staff = self.create_user('staff', is_staff=True)

    def create_user(self, username, **attrs):
        if attrs is None:
            attrs = {}
        user = User.objects.create_user(username, username + '@example.com', 'password')
        user.profile = Profile.objects.create(user=user)
        user.__dict__.update(**attrs)
        user.backend = self.session_backend
        user.save()
        return user

    def get_request_for_user(self, user):
        request = self.factory.get('/')
        request.user = self.user
        self.session_middleware.process_request(request)
        logout(request)
        return request

    def permissions_for_request(self, permissions_class, request):
        return permissions_class().check_permissions(request)

    def test_is_authenticated(self):
        request = self.get_request_for_user(self.user)
        self.assertFalse(self.permissions_for_request(AuthenticatedPermissions, request))
        login(request, self.user)
        self.assertTrue(self.permissions_for_request(AuthenticatedPermissions, request))

    def test_is_superuser(self):
        request = self.get_request_for_user(self.admin)
        self.assertFalse(self.permissions_for_request(AuthenticatedPermissions, request))
        login(request, self.admin)
        self.assertTrue(self.permissions_for_request(AuthenticatedPermissions, request))
        self.assertTrue(self.permissions_for_request(SuperuserPermissions, request))

    def test_is_staff(self):
        request_staff = self.get_request_for_user(self.staff)
        request_admin = self.get_request_for_user(self.admin)
        login(request_staff, self.staff)
        login(request_admin, self.admin)
        self.assertTrue(self.permissions_for_request(StaffPermissions, request_staff))
        self.assertFalse(self.permissions_for_request(StaffPermissions, request_admin))

    def test_staff_or_superuser(self):
        request_staff = self.get_request_for_user(self.staff)
        request_admin = self.get_request_for_user(self.admin)
        login(request_staff, self.staff)
        login(request_admin, self.admin)
        self.assertTrue(self.permissions_for_request(OrStaffSuperuserPermissions, request_staff))
        self.assertTrue(self.permissions_for_request(OrStaffSuperuserPermissions, request_admin))

    def test_staff_and_superuser(self):
        request_staff = self.get_request_for_user(self.staff)
        request_admin = self.get_request_for_user(self.admin)
        request_user = self.get_request_for_user(self.user)
        login(request_staff, self.staff)
        login(request_admin, self.admin)
        login(request_user, self.user)
        self.assertFalse(self.permissions_for_request(AndStaffSuperuserPermissions, request_staff))
        self.assertFalse(self.permissions_for_request(AndStaffSuperuserPermissions, request_admin))
        self.assertFalse(self.permissions_for_request(AndStaffSuperuserPermissions, request_user))
        self.admin.is_staff = True
        self.staff.is_superuser = True
        self.assertTrue(self.permissions_for_request(AndStaffSuperuserPermissions, request_staff))
        self.assertTrue(self.permissions_for_request(AndStaffSuperuserPermissions, request_admin))
        self.assertFalse(self.permissions_for_request(AndStaffSuperuserPermissions, request_user))

    def test_request_objects(self):
        request_user = self.get_request_for_user(self.user)
        request_admin = self.get_request_for_user(self.admin)
        login(request_user, self.user)
        self.assertFalse(self.permissions_for_request(IsPublicPermissions, request_user))
        self.assertFalse(self.permissions_for_request(IsPublicPermissions, request_admin))
        self.assertFalse(self.permissions_for_request(AuthenticatedPermissions, request_admin))
        self.user.get_profile().is_public = True
        self.assertTrue(self.permissions_for_request(IsPublicPermissions, request_user))
        self.assertFalse(self.permissions_for_request(IsPublicPermissions, request_admin))

    def test_negation_request_objects(self):
        request_user = self.get_request_for_user(self.user)
        request_admin = self.get_request_for_user(self.admin)
        login(request_user, self.user)
        login(request_admin, self.admin)
        self.assertTrue(self.permissions_for_request(AuthenticatedPermissions, request_user))
        self.assertTrue(self.permissions_for_request(AuthenticatedPermissions, request_admin))
        self.assertFalse(self.permissions_for_request(NegatePermissions, request_user))
        self.assertFalse(self.permissions_for_request(NegatePermissions, request_admin))
        self.user.get_profile().is_public = True
        self.admin.get_profile().is_public = True
        self.assertTrue(self.permissions_for_request(NegatePermissions, request_user))
        self.assertTrue(self.permissions_for_request(NegatePermissions, request_admin))

    def test_nested_permissions(self):
        request_admin = self.get_request_for_user(self.admin)
        self.assertFalse(self.permissions_for_request(NestedPermissions, request_admin))
        login(request_admin, self.admin)
        self.assertFalse(self.permissions_for_request(NestedPermissions, request_admin))
        self.admin.username = 'admin2'
        self.assertFalse(self.permissions_for_request(NestedPermissions, request_admin))
        self.admin.is_staff = True
        self.assertTrue(self.permissions_for_request(NestedPermissions, request_admin))

    def test_request_params(self):
        request_admin = self.get_request_for_user(self.admin)
        self.assertFalse(self.permissions_for_request(RequestParamPermissions, request_admin))
        login(request_admin, self.admin)
        self.assertTrue(self.permissions_for_request(RequestParamPermissions, request_admin))
