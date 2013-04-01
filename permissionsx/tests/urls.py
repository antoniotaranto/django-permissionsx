"""
PermissionsX - Authorization for Django Class-Based Views.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.conf.urls import (
    patterns,
    url,
)

from permissionsx.tests.views import (
    anonymous_view,
    login_view,
    is_authenticated_redirect_view,
    is_authenticated_view,
    request_context_redirect_view,
    request_context_redirect_authenticated_view,
    request_context_view,
    request_context_attribute_check_view,
)


SOMETHING_PK = '(?P<pk>[0-9]{1})'

urlpatterns = patterns('',
    url(r'^anonymous/', anonymous_view, name='anonymous'),
    url(r'^login/', login_view, name='login'),
    url(r'^is-authenticated-redirect/', is_authenticated_redirect_view, name='is_authenticated_redirect'),
    url(r'^is-authenticated/', is_authenticated_view, name='is_authenticated'),
    url(r'^request-context-redirect/{}/'.format(SOMETHING_PK), request_context_redirect_view, name='request_context_redirect'),
    url(r'^request-context-redirect-authenticated/{}/'.format(SOMETHING_PK), request_context_redirect_authenticated_view, name='request_context_redirect_authenticated'),
    url(r'^request-context/{}/'.format(SOMETHING_PK), request_context_view, name='request_context'),
    url(r'^request-context-attribute-check/{}/'.format(SOMETHING_PK), request_context_attribute_check_view, name='request_context_attribute_check'),
)
