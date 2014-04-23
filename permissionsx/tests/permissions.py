"""PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

from permissionsx.models import P
from permissionsx.models import Permissions


user_is_authenticated = P(user__is_authenticated=True)
user_is_staff = P(user__is_staff=True)
user_is_superuser = P(user__is_superuser=True)


OVERRIDE_TRUE = 'Override returns True'
OVERRIDE_FALSE = 'Override returns False'


def if_true_override():
    return OVERRIDE_TRUE


def if_false_override():
    return OVERRIDE_FALSE


class AuthenticatedPermissions(Permissions):

    rules = P(user__is_authenticated=True)


class SuperuserPermissions(Permissions):

    rules = user_is_superuser


class StaffPermissions(Permissions):

    rules = user_is_staff


class OrStaffSuperuserPermissions(Permissions):

    rules = user_is_staff | user_is_superuser


class AndStaffSuperuserPermissions(Permissions):

    rules = user_is_staff & user_is_superuser


class NegatePermissions(Permissions):

    rules = ~P(user__is_public=False) & ~P(user__is_authenticated=False)


class IsPublicPermissions(Permissions):

    rules = P(user__is_public=True)


class NestedPermissions(Permissions):

    rules = P(
        P(user__is_authenticated=True) &
        P(
            P(user__is_staff=True) &
            P(P(user__is_superuser=True) & P(user__username='admin2'))
        )
    )


class RequestParamPermissions(Permissions):

    def get_rules(self, request=None):
        return ~P(user__is_authenticated=False) & P(user__username=request.user.username)


class OverrideIfFalsePermissions(Permissions):

    rules = P(user__is_authenticated=True, if_false=if_false_override)


class OverrideIfTruePermissions(Permissions):

    rules = P(user__is_authenticated=True, if_true=if_true_override)


class OverrideIfTrueFalsePermissions(Permissions):

    rules = P(user__is_authenticated=True, if_true=if_true_override, if_false=if_false_override)


class NegatedOverrideIfTrueFalsePermissions(Permissions):

    rules = ~P(user__is_authenticated=True, if_true=if_true_override, if_false=if_false_override)


class NestedNegatedOverridePermissions(Permissions):

    rules = P(
        P(user__is_authenticated=False) &
        ~P(
            user__is_authenticated=True,
            if_true=if_true_override,
            if_false=if_false_override
        )
    )


class NestedNegatedPermissions(Permissions):

    rules = P(
        ~P(user__is_authenticated=False) &
        P(
            P(user__is_authenticated=True) |
            ~P(user__is_authenticated=False)
        )
    )


class UserAttributesDependentPermissions(Permissions):

    rules = P(user__username='user_username')
