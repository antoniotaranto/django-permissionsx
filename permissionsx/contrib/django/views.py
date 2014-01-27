"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

from django.core.exceptions import ImproperlyConfigured
from django.utils import importlib
from django.views.generic import RedirectView as DjangoRedirectView
from django.views.generic import View
from django.contrib import auth

from permissionsx import settings


class RedirectView(DjangoRedirectView):
    """Default view used when redirecting user with insufficient permissions."""

    permanent = False
    redirect_url = None

    def get_redirect_url(self, **kwargs):
        if self.redirect_url is None:
            self.redirect_url = settings.PERMISSIONSX_REDIRECT_URL
        if self.request.user.is_authenticated():
            return self.redirect_url
        return self.redirect_url + '?next=' + self.request.get_full_path()


class MessageRedirectView(RedirectView):
    """Inherits from :class:`RedirectView`. Displays message after redirect. Usage:
    ::
        class AccessDeniedView(MessageRedirectView):

            message = (messages.warning, 'Access Denied')

    """
    message = (None, None)

    def get_message(self, request=None):
        return self.message

    def get(self, request, *args, **kwargs):
        msg_func, msg = self.get_message(request)
        if msg is not None:
            msg_func(request, msg)
        return super(MessageRedirectView, self).get(request, *args, **kwargs)


class DjangoViewMixin(object):
    """Mixin required by any Django view used with permissions.

    :attr permissions: must be instance or a subclass of :class:`Permissions`.
    :attr permissions_response_class: must be a subclass of :class:`View`.

    """
    permissions = None
    permissions_response_class = RedirectView

    def dispatch(self, request, *args, **kwargs):
        if self.permissions is None:
            raise ImproperlyConfigured('"permissions" is not defined for {}'.format(self.__class__.__name__))
        check_result = self.permissions.check(request, **kwargs)
        # NOTE: Check if any of the permissions wanted to override default response.
        if hasattr(request, 'permissionsx_return_overrides'):
            if request.permissionsx_return_overrides:
                # NOTE: Execute override and pass View parameters.
                return request.permissionsx_return_overrides[0](request, *args, **kwargs)
        # NOTE: Access granted, return the requested view.
        if check_result:
            return super(DjangoViewMixin, self).dispatch(request, *args, **kwargs)
        elif settings.PERMISSIONSX_LOGOUT_IF_DENIED:
            auth.logout(request)
        # NOTE: Unauthorized.
        return self.permissions_response_class.as_view()(request, *args, **kwargs)


generic_module = importlib.import_module('django.views.generic')
for key in dir(generic_module):
    obj = getattr(generic_module, key)
    try:
        if issubclass(obj, View):
            new_view = type('Permissions' + key, (DjangoViewMixin, obj), {})
            globals()[new_view.__name__] = new_view
            del new_view
    except TypeError:
        pass
