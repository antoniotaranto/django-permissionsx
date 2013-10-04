"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized


__all__ = ['TastypieAuthorization']


class TastypieAuthorization(Authorization):

    def __init__(self, *args, **kwargs):
        super(TastypieAuthorization, self).__init__(*args, **kwargs)
        self.permissions = self.permissions_class()

    def read_list(self, object_list, bundle):
        if self.permissions.check_permissions(bundle.request):
            return object_list
        raise Unauthorized()

    def read_detail(self, object_list, bundle):
        return self.permissions.check_permissions(bundle.request)

    def create_list(self, object_list, bundle):
        if self.permissions.check_permissions(bundle.request):
            return object_list
        raise Unauthorized()

    def create_detail(self, object_list, bundle):
        return self.permissions.check_permissions(bundle.request)

    def update_list(self, object_list, bundle):
        if self.permissions.check_permissions(bundle.request):
            return object_list
        raise Unauthorized()

    def update_detail(self, object_list, bundle):
        return self.permissions.check_permissions(bundle.request)

    def delete_list(self, object_list, bundle):
        return self.permissions.check_permissions(bundle.request)

    def delete_detail(self, object_list, bundle):
        return self.permissions.check_permissions(bundle.request)
