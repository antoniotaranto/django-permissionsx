"""
PermissionsX - Authorization for Django Class-Based Views.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.views.generic import View
from django.http import HttpResponse

from permissionsx.tests.models import somethings


OK_RESPONSE = '200'
LOGIN_RESPONSE = 'LOGIN'


class DummyView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse(OK_RESPONSE)


class LoginView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse(LOGIN_RESPONSE)


class AnonymousView(DummyView):

    pass


class IsAuthenticatedView(DummyView):

    permissions = ['user__is_authenticated']


class IsAuthenticatedRedirectView(DummyView):

    permissions = ['user__is_authenticated->login']


class CommonRequestContext(object):

    @staticmethod
    def get_request_context(**kwargs):
        return {
            # NOTE: Just as an example, in real world this could be:
            # 'something': get_object_or_404(Something, pk=kwargs.get('pk')),
            'something': somethings[kwargs.get('pk')],
        }


class RequestContextView(DummyView, CommonRequestContext):

    permissions = ['actor__owns:something']


class RequestContextRedirectView(DummyView, CommonRequestContext):

    permissions = ['actor__owns:something->login']


class RequestContextRedirectAuthenticatedView(DummyView, CommonRequestContext):

    permissions = ['user__is_authenticated->login', 'actor__owns:something']


class RequestContextAttributeCheckView(DummyView, CommonRequestContext):

    permissions = ['actor__owns:something', 'something__is_active']


login_view = LoginView.as_view()
anonymous_view = AnonymousView.as_view()
is_authenticated_view = IsAuthenticatedView.as_view()
is_authenticated_redirect_view = IsAuthenticatedRedirectView.as_view()
request_context_view = RequestContextView.as_view()
request_context_redirect_view = RequestContextRedirectView.as_view()
request_context_redirect_authenticated_view = RequestContextRedirectAuthenticatedView.as_view()
request_context_attribute_check_view = RequestContextAttributeCheckView.as_view()