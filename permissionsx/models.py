"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.db.models.query_utils import Q
from django.core.exceptions import ImproperlyConfigured


class Permissions(object):

    def get_permissions(self, request=None):
        try:
            return self.permissions
        except AttributeError:
            raise ImproperlyConfigured('Missing permissions for class "{}"!'.format(self.__class__.__name__))


class P(Q):
    """
    Borrowed from `django.db.models.query_utils.Q`. Subclassing just in case.
    """
    pass


class AnonymousProfile(object):

    user = None
