"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

import logging

from django import template
from django.contrib import auth
from django.views.generic import RedirectView as DjangoRedirectView
from django.core.exceptions import ImproperlyConfigured

from permissionsx import settings
from permissionsx.utils import get_class


logger = logging.getLogger('permissionsx')


class RedirectView(DjangoRedirectView):

    permanent = False
    redirect_url = None

    def get_redirect_url(self, **kwargs):
        if self.redirect_url is None:
            self.redirect_url = settings.PERMISSIONSX_REDIRECT_URL
        if self.request.user.is_authenticated():
            return self.redirect_url
        return self.redirect_url + '?next=' + self.request.get_full_path()


class MessageRedirectView(RedirectView):

    message = (None, None)

    def get_message(self, request=None):
        return self.message

    def get(self, request, *args, **kwargs):
        msg_func, msg = self.get_message(request)
        if msg is not None:
            msg_func(request, msg)
        return super(MessageRedirectView, self).get(request, *args, **kwargs)


class DjangoViewMixin(object):

    permissions_class = None
    permissions_response_class = RedirectView

    def dispatch(self, request, *args, **kwargs):
        if hasattr(self, 'permissions_class'):
            permissions = self.permissions_class() if callable(self.permissions_class) else self.permissions_class
            if settings.PERMISSIONSX_DEBUG:
                logger.debug('View class: {}'.format(self.__class__.__name__))
                logger.debug('View permissions class: {}'.format(permissions.__class__.__name__))
            if permissions is None:
                raise ImproperlyConfigured('"permissions_class" is not defined for {}'.format(self.__class__.__name__))
            check_result = permissions.check_permissions(request, **kwargs)
            # NOTE: Check if any of the permissions checked want to override default response.
            if request.permissionsx_return_overrides:
                # NOTE: Perform return override and pass everything available, e.g. for customizing View responses.
                return request.permissionsx_return_overrides[0](request, *args, **kwargs)
            # NOTE: Access granted, return the requested view.
            if check_result:
                return super(DjangoViewMixin, self).dispatch(request, *args, **kwargs)
            elif settings.PERMISSIONSX_LOGOUT_IF_DENIED:
                auth.logout(request)
            # NOTE: Return default response for 401 - access couldn't be granted.
            return self.permissions_response_class.as_view()(request, *args, **kwargs)
        return super(DjangoViewMixin, self).dispatch(request, *args, **kwargs)


class DummyRequest(object):

    user = None

    def __init__(self, user=None):
        if user is not None:
            self.user = user


register = template.Library()


@register.assignment_tag(takes_context=True)
def permissions(context, permissions_path, **kwargs):
    module, _, name = permissions_path.rpartition('.')
    permissions_class = get_class(module, name)
    # NOTE: Dummy request keeps temporary template objects without affecting the real
    #       request. Otherwise iterating over them would change the object that was
    #       assigned at the view level.
    dummy_request = DummyRequest()
    dummy_request.user = context['user']
    granted = permissions_class().check_permissions(dummy_request, **kwargs)
    return granted
