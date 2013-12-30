"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
import copy
import logging

from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.signals import user_logged_in

from permissionsx import settings


logger = logging.getLogger('permissionsx')


class Permissions(object):
    """Base class for defining permissions. Usage:
    ::
        permissions_class = SuperuserPermissions

    Or when there is no need of reusing permissions in other parts of the code:
    ::
        permissions_class = Permissions(P(user__is_superuser=True))

    """
    permissions = None

    def __init__(self, *args, **kwargs):
        if args:
            if self.permissions is None:
                self.permissions = args[0]
            else:
                self.permissions = self.permissions & args[0]

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
            try:
                attr = getattr(cmp_obj, word)
            except AttributeError:
                # NOTE: If AttributeError happens here, it's probably because of
                #       anonymous user being passed for permission checking.
                #       In that case, deny by default. REVIEW once Django gets
                #       custom anonymous user models.
                return False
            partial = attr() if callable(attr) else attr
            cmp_obj = partial
        try:
            attr = getattr(cmp_obj, last_word)
            if callable(attr) and isinstance(argument, Arg):
                return attr(getattr(request, argument.argument))
            elif callable(attr):
                partial = attr()
            else:
                partial = attr
            if isinstance(argument, Cmp):
                argument = getattr(request, argument.argument)
        except AttributeError:
            # NOTE: If AttributeError happens here, it's probably because of
            #       anonymous user being passed for permission checking.
            #       In that case, deny by default. REVIEW once Django gets
            #       custom anonymous user models.
            return False
        return partial == argument

    def permissions_traversal(self, request, subtree):
        if hasattr(subtree, 'children'):
            children_results = []
            for child in subtree.children:
                if hasattr(child, 'children'):
                    children_results.append(self.permissions_traversal(request, child))
                else:
                    child_copy = copy.copy(child)
                    if_true = child_copy.pop('if_true', None)
                    if_false = child_copy.pop('if_false', None)
                    # NOTE: list() used for Python 3.x compatibility.
                    items = list(child_copy.items())[0]
                    result = self.permissions_evaluate(request, items[0], items[1])
                    if subtree.negated:
                        children_results.append(not result)
                    else:
                        children_results.append(result)
                    if result and if_true is not None:
                        request.permissionsx_return_overrides += [if_true]
                    if not result and if_false is not None:
                        request.permissionsx_return_overrides += [if_false]
            if subtree.connector == P.OR:
                return True in children_results
            else:
                return not False in children_results

    def get_permissions(self, request=None, **kwargs):
        """Used for overriding :attr:`permissions` if some of the values used for authorization
        must be compared with request object.

        """
        return self.permissions

    def get_combined_permissions(self, request, **kwargs):
        permissions = self.get_permissions(request, **kwargs)
        if self.permissions is not None and permissions is not None:
            permissions = self.permissions & permissions
        return permissions

    def check_permissions(self, request=None, *args, **kwargs):
        permissions = self.get_combined_permissions(request, **kwargs)
        if permissions:
            setattr(request, 'permissionsx_return_overrides', [])
            return self.permissions_traversal(request, permissions)
        return True


class P(object):
    """Based on `django.db.models.query_utils.Q` mixed with `django.utils.tree.Node`."""

    AND = '&'
    OR = '|'
    default = AND

    def __init__(self, children=None, connector=None, negated=False, **kwargs):
        if children is None and kwargs:
            children = [kwargs]
        elif isinstance(children, P):
            children = [children]
        self.children = children and copy.copy(children) or []
        self.connector = connector or self.default
        self.subtree_parents = []
        self.negated = negated

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
        obj = P()
        obj.add(self, self.AND)
        obj.negate()
        return obj

    def __str__(self):
        str_param = (self.connector, ','.join([str(c) for c in self.children]))
        if self.negated:
            return '(~({0}{1}))'.format(*str_param)
        return '({0}{1})'.format(*str_param)

    def __deepcopy__(self, memodict):
        obj = P(connector=self.connector, negated=self.negated)
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

    def _new_instance(self):
        return P(self.children, self.connector, self.negated)

    def add(self, node, conn_type):
        if node in self.children and conn_type == self.connector:
            return
        if len(self.children) < 2:
            self.connector = conn_type
        if self.connector == conn_type:
            if isinstance(node, P) and (node.connector == conn_type or len(node) == 1):
                self.children.extend(node.children)
            else:
                self.children.append(node)
        else:
            obj = self._new_instance()
            self.connector = conn_type
            self.children = [obj, node]

    def negate(self):
        new_instance = self._new_instance()
        new_instance.negated = not new_instance.negated
        self.children = [new_instance]
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
    """This is a wrapper class used with :class:`P` instances to change behaviour of
    :meth:`Permissions.permissions_evaluate` method. If :class:`Arg` is passed as a value
    of keyword argument, its :attr:`argument` attribute will be used to retrieve attribute
    of the request object, e.g.:
    ::
        P(user__get_profile__has_access_to=Arg('invoice'))

    Will translate to:
    ::
        is_authorized = request.user.get_profile().has_access_to(request.invoice)

    """
    def __init__(self, argument, request=None):
        self.argument = argument

    def __str__(self):
        return 'Arg({})'.format(self.argument)


class Cmp(object):
    """This is a wrapper class used with :class:`P` instances to change behaviour of
    :meth:`Permissions.permissions_evaluate` method. If :class:`Cmp` is passed as a value
    of keyword argument, its :attr:`argument` attribute will be used to retrieve attribute
    of the request object, e.g.:
    ::
        P(user__get_profile__equals_to=Cmp('invoice'))

    Will translate to:
    ::
        is_authorized = request.user.get_profile().equals_to == request.invoice

    """
    def __init__(self, argument, request=None):
        self.argument = argument

    def __str__(self):
        return 'Cmp({})'.format(self.argument)

