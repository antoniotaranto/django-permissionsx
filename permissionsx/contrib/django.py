"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

from django import template
from django.contrib import auth
from django.views.generic import RedirectView

from classytags.core import Options
from classytags.arguments import Argument
from classytags.arguments import MultiKeywordArgument
from classytags.helpers import Tag

from permissionsx import settings
from permissionsx.utils import get_class


__all__ = ['DjangoViewMixin']


class PermissionsRedirectView(RedirectView):

    permanent = False

    def get_redirect_url(self, **kwargs):
        if self.request.user.is_authenticated():
            return settings.PERMISSIONSX_REDIRECT_URL
        return settings.PERMISSIONSX_REDIRECT_URL + '?next=' + self.request.path


class DjangoViewMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if hasattr(self, 'permissions_class'):
            permissions = self.permissions_class()
            if permissions.check_permissions(request, **kwargs):
                return super(DjangoViewMixin, self).dispatch(request, *args, **kwargs)
            elif settings.PERMISSIONSX_LOGOUT_IF_DENIED:
                auth.logout(request)
            return PermissionsRedirectView.as_view()(request, *args, **kwargs)
        return super(DjangoViewMixin, self).dispatch(request, *args, **kwargs)


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
        granted = permissions_class().check_permissions(context['request'], **kwargs)
        if varname:
            context[varname] = granted
            return ''
        else:
            return granted

register.tag(Permissions)
