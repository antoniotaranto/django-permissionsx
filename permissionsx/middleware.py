"""
PermissionsX - Authorization for Django Class-Based Views.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from permissionsx.utils import get_class


class PermissionsXMiddleware(object):

    _views_cache = None

    def __init__(self):
        self._views_cache = {}

    def check_single_perm(self, request, permission):
        redirect_url_name = None
        if '->' in permission:
            permission, _, redirect_url_name = permission.rpartition('->')
        obj, method, argument = permission.split('__') + [None]
        if ':' in method:
            method, argument = method.split(':')
        try:
            request_obj = getattr(request, obj)
        except AttributeError:
            raise ImproperlyConfigured('Request has no "{}" attribute defined. '
                'Either install appropriate middleware or use static method get_request_context() to add a new attribute.'.format(obj))
        try:
            attr = getattr(request_obj, method)
        except AttributeError:
            raise ImproperlyConfigured('Object "{}" has no method "{}".'.format(obj, method))
        if argument and callable(attr):
            result = attr(getattr(request, argument))
        elif callable(attr):
            result = attr()
        elif not callable(attr):
            result = bool(attr)
        return result, redirect_url_name

    def check_permissions_or_mode(self, request, permissions):
        # NOTE: Now what with redirects? Which URL name should it take if two or more options?
        #       Assuming the last checked permissions is the one to be used, for sake of simplicity.
        conditions_met = False
        final_url_name = None
        for permission in permissions:
            result, redirect_url_name = self.check_single_perm(request, permission)
            if redirect_url_name is not None:
                final_url_name = redirect_url_name
            if result:
                conditions_met = True
        return conditions_met, final_url_name

    def check_permissions(self, request, permissions):
        for permission in permissions:
            # NOTE: [('user__is_A', 'user__is_B'), 'user__is_C'] <==> (User is A OR User is B) AND User is C
            is_or_perm = isinstance(permission, (list, tuple))
            check_func = is_or_perm and self.check_permissions_or_mode or self.check_single_perm
            result, redirect_url_name = check_func(request, permission)
            if not result:
                if redirect_url_name is not None:
                    return False, redirect_url_name
                else:
                    raise PermissionDenied            
        return True, None

    def process_view(self, request, view_func, view_args, view_kwargs):
        view_key = view_func.__module__ + '.' + view_func.__name__
        if not view_key in self._views_cache:
            try:
                view = get_class(view_func.__module__, view_func.__name__)
            except ImportError:
                # NOTE: This could be caused by wrapping view.
                return
            else:
                self._views_cache[view_key] = view
        else:
            view = self._views_cache[view_key]
        try:
            objects = view.get_request_context(request, **view_kwargs)
        except AttributeError:
            # NOTE: There are no additional objects to be pushed into request.
            pass
        else:
            request.__dict__.update(objects)
        try:
            allowed, redirect_url_name = self.check_permissions(request, view.permissions)
        except AttributeError:
            # NOTE: Apparently, permissions were not defined for this view.
            allowed, redirect_url_name = True, None
        if not allowed and redirect_url_name is not None:
            return HttpResponseRedirect(reverse(redirect_url_name) + '?next=' + request.path)
