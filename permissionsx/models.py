"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
import logging

from django.db.models.query_utils import Q
from django.core.exceptions import ImproperlyConfigured

from permissionsx import settings


logger = logging.getLogger('permissionsx')


class Permissions(object):

    permissions = None

    def permissions_evaluate(self, request, expression, argument=None):
        words = expression.split('__')
        word = words.pop(0)
        try:
            cmp_obj = getattr(request, word)
        except AttributeError:
            # NOTE: WSGIRequest has no `obj` attribute. Raise exception by
            #       default, this means something is wrong with permissions.
            raise ImproperlyConfigured('There is no request object matching "{}". Related to rule: "{}".'.format(word, expression))
        for word in words:
            attr = getattr(cmp_obj, word)
            try:
                partial = attr()
            except TypeError:
                # NOTE: Object not callable.
                partial = attr
            cmp_obj = partial
        result = cmp_obj == argument
        return result

    def tree_traversal(self, request, subtree):
        if hasattr(subtree, 'children'):
            children_results = []
            for child in subtree.children:
                if hasattr(child, 'children'):
                    children_results.append(self.tree_traversal(request, child))
                else:
                    result = self.permissions_evaluate(request, child[0], child[1])
                    if settings.PERMISSIONSX_DEBUG:
                        logger.debug('Permissions check: {}={} is {}'.format(child[0], child[1], result))
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
