"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.contrib import auth
from django.views.generic import RedirectView

from permissionsx import settings
from permissionsx.core import PermissionBase


class PermissionsRedirectView(RedirectView):

    permanent = False

    def get_redirect_url(self, **kwargs):
        return settings.PERMISSIONSX_REDIRECT_URL + '?next=' + self.request.path


class PermissionsViewMixin(PermissionBase):

    def dispatch(self, request, *args, **kwargs):
        if self.check_permissions(request):
            return super(PermissionsViewMixin, self).dispatch(request, *args, **kwargs)
        else:
            if settings.PERMISSIONSX_LOGOUT_IF_DENIED:
                auth.logout(self.request)
            return PermissionsRedirectView.as_view(**self.kwargs)(request, *args, **kwargs)
