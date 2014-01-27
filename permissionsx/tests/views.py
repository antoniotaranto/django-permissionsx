"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

from django.views.generic import (
    TemplateView,
    View,
)
from django.contrib import messages
from django.http import HttpResponse

from permissionsx.models import Permissions
from permissionsx.models import P
from permissionsx.contrib.django.views import (
    PermissionsTemplateView,
    MessageRedirectView,
)
from permissionsx.tests.permissions import (
    AuthenticatedPermissions,
    OrStaffSuperuserPermissions,
    SuperuserPermissions,
)


class SimpleGetView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse(str(args) + str(kwargs))


class LoginView(TemplateView):

    template_name = 'tests/login.html'


class Login2View(TemplateView):

    template_name = 'tests/login2.html'


class AuthenticatedView(PermissionsTemplateView):

    template_name = 'tests/passed.html'
    permissions = AuthenticatedPermissions()


class AccessDeniedView(MessageRedirectView):

    message = (messages.warning, 'Access Denied')


class ResponseClassView(PermissionsTemplateView):

    template_name = 'tests/passed.html'
    permissions = AuthenticatedPermissions()
    permissions_response_class = AccessDeniedView


class GetProfileView(PermissionsTemplateView):

    template_name = 'tests/passed.html'
    permissions = OrStaffSuperuserPermissions()


class SuperuserView(PermissionsTemplateView):

    template_name = 'tests/passed.html'
    permissions = SuperuserPermissions()


class OverridesIfFalseView(PermissionsTemplateView):

    template_name = 'tests/passed.html'
    permissions = Permissions(
        P(user__is_authenticated=True) &
        P(user__is_superuser=True, if_false=Login2View.as_view())
    )


class OverridesIfTrueView(PermissionsTemplateView):

    template_name = 'tests/passed.html'
    permissions = Permissions(
        P(user__is_authenticated=True) | P(
            P(user__is_authenticated=True) &
            P(user__is_superuser=True, if_true=TemplateView.as_view(template_name='tests/welcome.html'))
        )
    )


class OverridesBothView(PermissionsTemplateView):

    template_name = 'tests/passed.html'
    permissions = Permissions(
        P(user__is_authenticated=True, if_false=Login2View.as_view()) |
        P(user__is_superuser=True, if_true=TemplateView.as_view(template_name='tests/welcome.html'))
    )


class SubsequentOverridesView(PermissionsTemplateView):

    template_name = 'tests/passed.html'
    permissions = Permissions(
        P(user__is_authenticated=True, if_false=Login2View.as_view()) |
        P(user__is_superuser=True, if_false=TemplateView.as_view(template_name='tests/welcome.html'))
    )


class MenuView(PermissionsTemplateView):

    template_name = 'tests/menu.html'
    permissions = AuthenticatedPermissions()


login_view = LoginView.as_view()
login2_view = Login2View.as_view()
authenticated_view = AuthenticatedView.as_view()
response_class_view = ResponseClassView.as_view()
get_profile_view = GetProfileView.as_view()
superuser_view = SuperuserView.as_view()
overrides_if_false_view = OverridesIfFalseView.as_view()
overrides_if_true_view = OverridesIfTrueView.as_view()
overrides_both_view = OverridesBothView.as_view()
subsequent_overrides_view = SubsequentOverridesView.as_view()
menu_view = MenuView.as_view()
