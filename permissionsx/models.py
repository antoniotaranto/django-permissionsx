"""PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

import copy

from django.core.exceptions import ImproperlyConfigured


class Permissions(object):
    """Base class for defining permissions. Usage:
    ::
        permissions = SuperuserPermissions

    Or when there is no need of reusing permissions in other parts
    of the code:
    ::
        permissions = Permissions(P(user__is_superuser=True))
    """

    rules = None

    def __init__(self, *args, **kwargs):
        if self.rules is None:
            self.rules = P()
        if args:
            self.rules = self.rules & args[0]

    def rules_evaluate(self, request, exp, argument=None):
        words = exp.split('__')
        word = words.pop(0)
        try:
            cmp_obj = getattr(request, word)
        except AttributeError:
            # NOTE: WSGIRequest has no `obj` attribute. Raise exception by
            #       default, this means something is wrong with permissions.
            raise ImproperlyConfigured(
                'There is no request object matching "{0}". Related to rule: "{1}" in class "{2}".'
                .format(word, exp, self.__class__.__name__)
            )
        last_word = words.pop()
        for word in words:
            try:
                attr = getattr(cmp_obj, word)
            except AttributeError:
                # NOTE: If AttributeError happens here, it's probably because
                #       of anonymous user being passed for rules checking.
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
            # NOTE: If AttributeError happens here, it's probably because
            #       of anonymous user being passed for rules checking.
            #       In that case, deny by default. REVIEW once Django gets
            #       custom anonymous user models.
            return False
        return partial == argument

    def rules_traversal(self, request, exp):
        children_results = []
        for child in exp.children:
            if isinstance(child, P):
                result = self.rules_traversal(request, child)
            else:
                rule = [i for i in child.items() if i[0] not in ['if_false', 'if_true']]
                if rule:
                    result = self.rules_evaluate(request, *rule[0])
                if request.permissionsx_return_overrides is None:
                    if_true = child.get('if_true', None)
                    if_false = child.get('if_false', None)
                    if result and if_true is not None:
                        request.permissionsx_return_overrides = if_true
                    if not result and if_false is not None:
                        request.permissionsx_return_overrides = if_false
            children_results.append(result)
        if exp.connector == P.OR:
            result = True in children_results
        else:
            result = False not in children_results
        if exp.negated:
            result = not result
        return result

    def get_rules(self, request=None, **kwargs):
        """Used for overriding :attr:`rules`."""
        return P()

    def get_combined_rules(self, request, **kwargs):
        rules = self.get_rules(request, **kwargs)
        if not isinstance(rules, P):
            raise TypeError('Method `get_rules` must return P instance!')
        return self.rules & rules

    def check(self, request=None, *args, **kwargs):
        rules = self.get_combined_rules(request, **kwargs)
        if rules:
            setattr(request, 'permissionsx_return_overrides', None)
            return self.rules_traversal(request, rules)
        return True


class P(object):
    """Base building block for defining rules.

    Based on `django.db.models.query_utils.Q` mixed with
    `django.utils.tree.Node`.
    """

    AND = '&'
    OR = '|'
    default = AND

    def __init__(self, children=None, connector=None, negated=False, **kwargs):
        if children is None and kwargs:
            children = [kwargs]
        elif isinstance(children, P):
            children = [children]
            if kwargs:
                children.append(kwargs)
        self.children = children and copy.copy(children) or []
        self.connector = connector or self.default
        self.subtree_parents = []
        self.negated = negated

    def _combine(self, other, conn):
        """Derived from `Q`."""
        if not isinstance(other, P):
            raise TypeError(other)
        obj = P()
        obj.add(self, conn)
        obj.add(other, conn)
        return obj

    def __or__(self, other):
        """Derived from `Q`."""
        return self._combine(other, self.OR)

    def __and__(self, other):
        """Derived from `Q`."""
        return self._combine(other, self.AND)

    def __invert__(self):
        """Derived from `Q`."""
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

    def __nonzero__(self):  # NOTE: Python 2 compatibility
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
    """Resolves string to an attribute of the request object.

    A wrapper class used with :class:`P` instances to change behaviour
    of :meth:`Permissions.rules_evaluate` method.

    If :class:`Arg` is passed, it will be used an argument for the
    method defined in the rule (i.e. the last part of the keyword
    argument name), e.g.:
    ::
        P(user__has_access_to=Arg('invoice'))

    Will translate to:
    ::
        is_authorized = request.user.has_access_to(request.invoice)
    """

    def __init__(self, argument, request=None):
        self.argument = argument

    def __str__(self):
        return 'Arg({0})'.format(self.argument)


class Cmp(object):
    """Resolves string to an attribute of the request object.

    A wrapper class used with :class:`P` instances to change behaviour
    of :meth:`Permissions.rules_evaluate` method.

    If :class:`Cmp` is passed, it will be used to retrieve attribute of
    the request object, e.g.:
    ::
        P(user__equals_to=Cmp('invoice'))

    Will translate to:
    ::
        is_authorized = (request.user.equals_to == request.invoice)
    """

    def __init__(self, argument, request=None):
        self.argument = argument

    def __str__(self):
        return 'Cmp({0})'.format(self.argument)
