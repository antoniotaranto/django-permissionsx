"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

import copy
import logging

from django import template
from django.contrib import auth
from django.views.generic import RedirectView as DjangoRedirectView
from django.core.exceptions import ImproperlyConfigured

from permissionsx import settings
from permissionsx.utils import get_class


logger = logging.getLogger('permissionsx')


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

    :attr permissions_class: must be instance or a subclass of :class:`Permissions`.
    :attr permissions_response_class: must be a subclass of :class:`View`.

    """
    permissions_class = None
    permissions_response_class = RedirectView

    def dispatch(self, request, *args, **kwargs):
        permissions = self.permissions_class() if callable(self.permissions_class) else self.permissions_class
        if settings.PERMISSIONSX_DEBUG:
            logger.debug('View class: {}'.format(self.__class__.__name__))
            logger.debug('View permissions class: {}'.format(permissions.__class__.__name__))
        if permissions is None:
            raise ImproperlyConfigured('"permissions_class" is not defined for {}'.format(self.__class__.__name__))
        check_result = permissions.check_permissions(request, **kwargs)
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


class DummyRequest(object):
    """This class is used internally with Django templates to isolate permission
    checks from original :class:`HttpRequest` context.

    """
    user = None

    def __init__(self, user=None):
        if user is not None:
            self.user = user


register = template.Library()


@register.assignment_tag(takes_context=True)
def permissions(context, permissions_path, **kwargs):
    """Django template tag for checking permissions inside templates. Usage:
    ::

        {% load permissionsx_tags %}
        {% permissions 'newspaper.profiles.permissions.AuthorPermissions' as user_is_author %}

    """
    module, _, name = permissions_path.rpartition('.')
    permissions_class = get_class(module, name)
    # NOTE: Dummy request keeps temporary template objects without affecting the real
    #       request. Otherwise iterating over them would change the object that was
    #       assigned at the view level.
    if 'request' in context:
        dummy_request = copy.copy(context['request'])
    else:
        dummy_request = DummyRequest()
        dummy_request.user = context['user']
    try:
        granted = permissions_class().check_permissions(dummy_request, **kwargs)
    except AttributeError:
        # NOTE: AttributeError is _usually_ related to anonymous user being
        #       used for checking permissions. TODO: Should be reviewed once
        #       Django custom user model gets its anonymous counterpart.
        return False
    return granted
