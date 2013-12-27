"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.views.generic import (
    TemplateView,
    )
from django.contrib import messages

from permissionsx.models import Permissions
from permissionsx.models import P
from permissionsx.contrib.django import DjangoViewMixin
from permissionsx.contrib.django import MessageRedirectView
from permissionsx.tests.permissions import (
    AuthenticatedPermissions,
    OrStaffSuperuserPermissions,
    SuperuserPermissions,
)


class LoginView(TemplateView):

    template_name = 'tests/login.html'


class Login2View(TemplateView):

    template_name = 'tests/login2.html'


class AuthenticatedView(DjangoViewMixin, TemplateView):

    template_name = 'tests/passed.html'
    permissions_class = AuthenticatedPermissions


class AccessDeniedView(MessageRedirectView):

    message = (messages.warning, 'Access Denied')


class ResponseClassView(DjangoViewMixin, TemplateView):

    template_name = 'tests/passed.html'
    permissions_class = AuthenticatedPermissions
    permissions_response_class = AccessDeniedView


class GetProfileView(DjangoViewMixin, TemplateView):

    template_name = 'tests/passed.html'
    permissions_class = OrStaffSuperuserPermissions


class SuperuserView(DjangoViewMixin, TemplateView):

    template_name = 'tests/passed.html'
    permissions_class = SuperuserPermissions


class OverridesIfFalseView(DjangoViewMixin, TemplateView):

    template_name = 'tests/passed.html'
    permissions_class = Permissions(
        P(user__is_authenticated=True) &
        P(user__is_superuser=True, if_false=Login2View.as_view())
    )


class OverridesIfTrueView(DjangoViewMixin, TemplateView):

    template_name = 'tests/passed.html'
    permissions_class = Permissions(
        P(user__is_authenticated=True) | P(
            P(user__is_authenticated=True) &
            P(user__is_superuser=True, if_true=TemplateView.as_view(template_name='tests/welcome.html'))
        )
    )


class OverridesBothView(DjangoViewMixin, TemplateView):

    template_name = 'tests/passed.html'
    permissions_class = Permissions(
        P(user__is_authenticated=True, if_false=Login2View.as_view()) |
        P(user__is_superuser=True, if_true=TemplateView.as_view(template_name='tests/welcome.html'))
    )


class SubsequentOverridesView(DjangoViewMixin, TemplateView):

    template_name = 'tests/passed.html'
    permissions_class = Permissions(
        P(user__is_authenticated=True, if_false=Login2View.as_view()) |
        P(user__is_superuser=True, if_false=TemplateView.as_view(template_name='tests/welcome.html'))
    )


class MenuView(DjangoViewMixin, TemplateView):

    template_name = 'tests/menu.html'
    permissions_class = AuthenticatedPermissions


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
