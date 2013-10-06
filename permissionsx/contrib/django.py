"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

from django import template
from django.contrib import auth
from django.contrib import messages
from django.views.generic import RedirectView as DjangoRedirectView
from django.views.generic import View

from classytags.core import Options
from classytags.arguments import Argument
from classytags.arguments import MultiKeywordArgument
from classytags.helpers import Tag

from permissionsx import settings
from permissionsx.utils import get_class


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
            permissions = self.permissions_class()
            if permissions.check_permissions(request, **kwargs):
                return super(DjangoViewMixin, self).dispatch(request, *args, **kwargs)
            elif settings.PERMISSIONSX_LOGOUT_IF_DENIED:
                auth.logout(request)
            return self.permissions_response_class.as_view()(request, *args, **kwargs)
        return super(DjangoViewMixin, self).dispatch(request, *args, **kwargs)



class DummyRequest(object):

    user = None


register = template.Library()


class Permissions(Tag):

    options = Options(
        Argument('permissions_path'),
        MultiKeywordArgument('kwargs', required=False),
        'as',
        Argument('varname', required=False, resolve=False)
    )

    def render_tag(self, context, permissions_path, varname, kwargs=None):
        if kwargs is None:
            kwargs = {}
        module, _, name = permissions_path.rpartition('.')
        permissions_class = get_class(module, name)
        # NOTE: Dummy request keeps temporary template objects without affecting the real
        #       request. Otherwise iterating over them would change the object that was
        #       assigned at the view level.
        dummy_request = DummyRequest()
        dummy_request.user = context['user']
        granted = permissions_class().check_permissions(dummy_request, **kwargs)
        if varname:
            context[varname] = granted
            return ''
        else:
            return granted

register.tag(Permissions)
