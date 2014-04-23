"""PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized


class TastypieAuthorization(Authorization):
    """Inherits from :class:`tastypie.authorization.Authorization`.

    Usage:
    ::
        class StaffOnlyAuthorization(TastypieAuthorization):

            permissions = StaffPermissions()
    """

    def read_list(self, object_list, bundle):
        if self.permissions.check(bundle.request):
            return object_list
        raise Unauthorized()

    def read_detail(self, object_list, bundle):
        return self.permissions.check(bundle.request)

    def create_list(self, object_list, bundle):
        if self.permissions.check(bundle.request):
            return object_list
        raise Unauthorized()

    def create_detail(self, object_list, bundle):
        return self.permissions.check(bundle.request)

    def update_list(self, object_list, bundle):
        if self.permissions.check(bundle.request):
            return object_list
        raise Unauthorized()

    def update_detail(self, object_list, bundle):
        return self.permissions.check(bundle.request)

    def delete_list(self, object_list, bundle):
        return self.permissions.check(bundle.request)

    def delete_detail(self, object_list, bundle):
        return self.permissions.check(bundle.request)
