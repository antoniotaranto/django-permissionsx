"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

from django.conf import settings
from django.conf.urls import (
    include,
    patterns,
    url,
)

import debug_toolbar
from tastypie.api import Api
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie.exceptions import Unauthorized

from permissionsx.contrib.tastypie import TastypieAuthorization
from permissionsx.tests.models import TestObject
from permissionsx.tests.permissions import (
    AuthenticatedPermissions,
    SuperuserPermissions,
)
from permissionsx.tests.views import (
    authenticated_view,
    get_profile_view,
    login_view,
    login2_view,
    menu_view,
    overrides_both_view,
    overrides_if_false_view,
    overrides_if_true_view,
    response_class_view,
    subsequent_overrides_view,
    superuser_view,
)


class SuperuserOnlyAuthorization(TastypieAuthorization):

    permissions = SuperuserPermissions()


class UpdatingOnlyAuthorization(TastypieAuthorization):

    permissions = AuthenticatedPermissions()

    def create_list(self, object_list, bundle):
        raise Unauthorized()

    def update_list(self, object_list, bundle):
        raise Unauthorized()

    def update_detail(self, object_list, bundle):
        return AuthenticatedPermissions().check(bundle.request)

    def delete_list(self, object_list, bundle):
        raise Unauthorized()

    def delete_detail(self, object_list, bundle):
        raise Unauthorized()


class TestSuperuserResource(ModelResource):

    class Meta:
        authorization = SuperuserOnlyAuthorization()
        queryset = TestObject.objects.all()
        fields = ('id', 'title')
        serializer = Serializer()


class TestOverrideResource(ModelResource):

    class Meta:
        authorization = UpdatingOnlyAuthorization()
        queryset = TestObject.objects.all()
        fields = ('id', 'title')
        serializer = Serializer()


v1_api = Api(api_name='v1')
v1_api.register(TestSuperuserResource())
v1_api.register(TestOverrideResource())


urlpatterns = patterns('',
    url(r'^accounts/login/$', login_view, name='auth_login'),
    url(r'^accounts/login2/$', login2_view, name='login2'),
    url(r'^authenticated/$', authenticated_view, name='authenticated'),
    url(r'^response-class/$', response_class_view, name='response_class'),
    url(r'^get-profile/$', get_profile_view, name='get_profile'),
    url(r'^superuser/$', superuser_view, name='superuser'),
    url(r'^overrides-if-false/$', overrides_if_false_view, name='overrides_if_false'),
    url(r'^overrides-if-true/$', overrides_if_true_view, name='overrides_if_true'),
    url(r'^overrides-both/$', overrides_both_view, name='overrides_both'),
    url(r'^subsequent-overrides/$', subsequent_overrides_view, name='subsequent_overrides'),
    url(r'^menu/$', menu_view, name='menu'),
    url(r'^api/', include(v1_api.urls)),
    url(r'^__debug__/', include(debug_toolbar.urls)),
)
