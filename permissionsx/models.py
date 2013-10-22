"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
import copy
import logging

from django.core.exceptions import ImproperlyConfigured
from django.utils import six

from permissionsx import settings


logger = logging.getLogger('permissionsx')


class Permissions(object):

    permissions = None

    def __init__(self, *args, **kwargs):
        if self.permissions is None and args:
            self.permissions = args[0]
        if 'if_false' in kwargs:
            self.permissions.if_false = kwargs.get('if_false')
        if 'if_true' in kwargs:
            self.permissions.if_true = kwargs.get('if_true')

    def permissions_evaluate(self, request, expression, argument=None):
        words = expression.split('__')
        word = words.pop(0)
        try:
            cmp_obj = getattr(request, word)
        except AttributeError:
            # NOTE: WSGIRequest has no `obj` attribute. Raise exception by
            #       default, this means something is wrong with permissions.
            raise ImproperlyConfigured('There is no request object matching "{}". Related to rule: "{}" in class "{}".'.format(word, expression, self.__class__.__name__))
        last_word = words.pop()
        for word in words:
            attr = getattr(cmp_obj, word)
            partial = attr() if callable(attr) else attr
            cmp_obj = partial
        attr = getattr(cmp_obj, last_word)
        if callable(attr) and isinstance(argument, Arg):
            return attr(getattr(request, argument.argument))
        elif callable(attr):
            partial = attr()
        else:
            partial = attr
        return partial == argument

    def tree_traversal(self, request, subtree, return_overrides):
        if hasattr(subtree, 'children'):
            children_results = []
            for child in subtree.children:
                if hasattr(child, 'children'):
                    children_results.append(self.tree_traversal(request, child, return_overrides))
                else:
                    result = self.permissions_evaluate(request, child[0], child[1])
                    if settings.PERMISSIONSX_DEBUG:
                        logger.debug('Permissions check: {}={} is {}'.format(child[0], child[1], result))
                    if subtree.negated:
                        children_results.append(not result)
                    else:
                        children_results.append(result)
                    if subtree.if_true:
                        return_overrides[True] = subtree.if_true
                    if subtree.if_false:
                        return_overrides[False] = subtree.if_false
            if subtree.connector == 'OR':
                boolean_result = True in children_results
            else:
                boolean_result = not False in children_results
            return boolean_result

    def get_permissions(self, request=None):
        return self.permissions

    def set_request_objects(self, request, **kwargs):
        pass

    def check_permissions(self, request=None, **kwargs):
        self.set_request_objects(request, **kwargs)
        permissions = self.get_permissions(request)
        if permissions:
            return_overrides = {True: None, False: None}
            # NOTE: Passing pointer to `return_overrides`.
            boolean_result = self.tree_traversal(request, permissions, return_overrides)
            setattr(request, 'permissionsx_return_overrides', return_overrides)
            return boolean_result
        return True


class P(object):
    """ Based on `django.db.models.query_utils.Q` mixed with `django.utils.tree.Node`. """

    AND = 'AND'
    OR = 'OR'
    default = AND

    def __init__(self, children=None, connector=None, negated=False, if_false=None, if_true=None, *args, **kwargs):
        if children is None:
            children = list(args) + list(six.iteritems(kwargs))
        elif isinstance(children, P):
            children = [children]
        self.children = children and children[:] or []
        self.connector = connector or self.default
        self.subtree_parents = []
        self.negated = negated
        self.if_false = if_false
        self.if_true = if_true

    def _combine(self, other, conn):
        """ Derived from `Q`. """
        if not isinstance(other, P):
            raise TypeError(other)
        obj = P()
        obj.add(self, conn)
        obj.add(other, conn)
        return obj

    def __or__(self, other):
        """ Derived from `Q`. """
        return self._combine(other, self.OR)

    def __and__(self, other):
        """ Derived from `Q`. """
        return self._combine(other, self.AND)

    def __invert__(self):
        """ Derived from `Q`. """
        obj = self._new_instance()
        obj.add(self, self.AND)
        obj.negate()
        return obj

    def __str__(self):
        if self.negated:
            return '(NOT (%s: %s))' % (self.connector, ', '.join([str(c) for c
                    in self.children]))
        return '(%s: %s)' % (self.connector, ', '.join([str(c) for c in
                self.children]))

    def __deepcopy__(self, memodict):
        obj = P(connector=self.connector, negated=self.negated, if_false=self.if_false, if_true=self.if_true)
        obj.children = copy.deepcopy(self.children, memodict)
        obj.subtree_parents = copy.deepcopy(self.subtree_parents, memodict)
        return obj

    def __len__(self):
        return len(self.children)

    def __bool__(self):
        return bool(self.children)

    def __nonzero__(self):      # Python 2 compatibility
        return type(self).__bool__(self)

    def __contains__(self, other):
        return other in self.children

    def _new_instance(self, negate=False):
        negated = not self.negated if negate else self.negated
        return P(self.children, self.connector, negated, self.if_false, self.if_true)

    def add(self, node, conn_type):
        if node in self.children and conn_type == self.connector:
            return
        if len(self.children) < 2:
            self.connector = conn_type
        if self.connector == conn_type:
            if isinstance(node, P) and (node.connector == conn_type or len(node) == 1):
                if node.if_false:
                    self.if_false = node.if_false
                if node.if_true:
                    self.if_true = node.if_true
                self.children.extend(node.children)
            else:
                self.children.append(node)
        else:
            obj = self._new_instance()
            self.connector = conn_type
            self.children = [obj, node]

    def negate(self):
        self.children = [self._new_instance(negate=True)]
        self.connector = self.default

    def start_subtree(self, conn_type):
        if len(self.children) == 1:
            self.connector = conn_type
        elif self.connector != conn_type:
            self.children = [self._new_instance()]
            self.connector = conn_type
            self.negated = False
        self.subtree_parents.append(self._new_instance())
        self.connector = self.default
        self.negated = False
        self.children = []

    def end_subtree(self):
        obj = self.subtree_parents.pop()
        node = P(self.children, self.connector)
        self.connector = obj.connector
        self.negated = obj.negated
        self.children = obj.children
        self.children.append(node)


class Arg(object):

    def __init__(self, argument):
        self.argument = argument
