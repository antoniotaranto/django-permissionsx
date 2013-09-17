"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.core.exceptions import ImproperlyConfigured

from permissionsx.models import P


class PermissionBase(object):

    permissions = None

    def permissions_evaluate(self, request, expression, argument=None):
        obj, method = expression.split('__')
        try:
            request_obj = getattr(request, obj)
        except AttributeError:
            # NOTE: WSGIRequest has no `obj` attribute. Raise exception by
            #       default, this means something is wrong with permissions.
            raise ImproperlyConfigured('There is no request object matching "{}". Related to rule: "{}".'.format(obj, expression))
        attr = getattr(request_obj, method)
        try:
            result = attr()
        except TypeError:
            # NOTE: Object not callable.
            result = attr
        return result == argument

    def tree_traversal(self, request, subtree):
        if hasattr(subtree, 'children'):
            children_results = []
            for child in subtree.children:
                if hasattr(child, 'children'):
                    children_results.append(self.tree_traversal(request, child))
                else:
                    result = self.permissions_evaluate(request, child[0], child[1])
                    if subtree.negated:
                        children_results.append(not result)
                    else:
                        children_results.append(result)
            if subtree.connector == 'OR':
                return True in children_results
            else:
                return not False in children_results

    def get_permissions_obj(self, request, permissions):
        if isinstance(permissions, P):
            return permissions
        else:
            # NOTE: In case of Django class-based views `self.request` could
            #       be used here. Request is passed for consistency with apps.
            return permissions().get_permissions(request)

    def check_permissions(self, request=None, overridden_permissions=None):
        if overridden_permissions is not None:
            permissions = self.get_permissions_obj(request, overridden_permissions)
        else:
            permissions = self.get_permissions_obj(request, self.permissions)
        return self.tree_traversal(request, permissions)
