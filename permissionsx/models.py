"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.db.models.query_utils import Q
from django.core.exceptions import ImproperlyConfigured


class Permissions(object):

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

    def get_permissions(self, request=None):
        return self.permissions

    def set_request_objects(self, request, **kwargs):
        pass

    def check_permissions(self, request=None, **kwargs):
        self.set_request_objects(request, **kwargs)
        permissions = self.get_permissions(request)
        if permissions:
            return self.tree_traversal(request, permissions)
        return True


class P(Q):
    """
    Borrowed from `django.db.models.query_utils.Q`. Subclassing just in case.
    """
    pass
