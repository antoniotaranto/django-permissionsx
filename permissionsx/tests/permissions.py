"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from permissionsx.models import P
from permissionsx.models import Permissions
from permissionsx.tests.models import AnonymousProfile


user_is_authenticated = P(user__is_authenticated=True)
user_is_staff = P(user__is_staff=True)
user_is_superuser= P(user__is_superuser=True)


class AuthenticatedPermissions(Permissions):

    permissions = P(user__is_authenticated=True)


class SuperuserPermissions(Permissions):

    permissions = user_is_superuser


class StaffPermissions(Permissions):

    permissions = user_is_staff


class OrStaffSuperuserPermissions(Permissions):

    permissions = user_is_staff | user_is_superuser


class AndStaffSuperuserPermissions(Permissions):

    permissions = user_is_staff & user_is_superuser


class ProfilePermissions(Permissions):

    def set_request_objects(self, request, **kwargs):
        if request.user.is_authenticated():
            request.profile = request.user.get_profile()
        else:
            request.profile = AnonymousProfile()


class NegatePermissions(ProfilePermissions):

    permissions = ~P(profile__is_public=False) & ~P(user__is_authenticated=False)


class IsPublicPermissions(ProfilePermissions):

    permissions = P(profile__is_public=True)


class NestedPermissions(Permissions):

    permissions = P(P(user__is_authenticated=True) & P(P(user__is_staff=True) & P(P(user__is_superuser=True) & P(user__username='admin2'))))


class RequestParamPermissions(Permissions):

    def get_permissions(self, request=None):
        return ~P(user__is_authenticated=False) & P(user__username=request.user.username)