"""
PermissionsX - Authorization for Django Class-Based Views.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from permissionsx.utils import get_class


class PermissionsXMiddleware(object):

    _views_cache = None

    def __init__(self):
        self._views_cache = {}

    def check_permissions(self, request, permissions):
        for perm in permissions:
            redirect_url_name = None
            if '->' in perm:
                perm, _, redirect_url_name = perm.rpartition('->')
            obj, method, argument = perm.split('__') + [None]
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
            objects = view.get_request_context(**view_kwargs)
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
