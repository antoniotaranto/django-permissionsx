"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from permissionsx.core import PermissionBase

from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized


class PermissionsAuthorization(PermissionBase, Authorization):

    def read_list(self, object_list, bundle):
        if self.check_permissions(bundle.request):
            return object_list
        raise Unauthorized()

    def read_detail(self, object_list, bundle):
        return self.check_permissions(bundle.request)

    def create_list(self, object_list, bundle):
        if self.check_permissions(bundle.request):
            return object_list
        raise Unauthorized()

    def create_detail(self, object_list, bundle):
        return self.check_permissions(bundle.request)

    def update_list(self, object_list, bundle):
        if self.check_permissions(bundle.request):
            return object_list
        raise Unauthorized()

    def update_detail(self, object_list, bundle):
        return self.check_permissions(bundle.request)

    def delete_list(self, object_list, bundle):
        return self.check_permissions(bundle.request)

    def delete_detail(self, object_list, bundle):
        return self.check_permissions(bundle.request)


