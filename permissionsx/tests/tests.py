"""PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

import json
import mock

from django.contrib import auth
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.test.utils import override_settings

from permissionsx.contrib.django.views import (
    DjangoViewMixin,
    RedirectView,
)
from permissionsx.models import (
    Arg,
    P,
    Permissions,
)
from permissionsx.contrib.django.templatetags import permissions
from permissionsx.tests.models import TestObject
from permissionsx.tests.permissions import (
    if_false_override,
    if_true_override,
    OVERRIDE_FALSE,
    OVERRIDE_TRUE,
)
from permissionsx.tests.permissions import (
    AndStaffSuperuserPermissions,
    AuthenticatedPermissions,
    IsPublicPermissions,
    OrStaffSuperuserPermissions,
    OverrideIfFalsePermissions,
    OverrideIfTruePermissions,
    OverrideIfTrueFalsePermissions,
    NegatePermissions,
    NegatedOverrideIfTrueFalsePermissions,
    NestedNegatedOverridePermissions,
    NestedNegatedPermissions,
    NestedPermissions,
    RequestParamPermissions,
    StaffPermissions,
    SuperuserPermissions,
    user_is_authenticated,
    user_is_staff,
    user_is_superuser,
)
from permissionsx.tests.utils import UtilityTestCase
from permissionsx.tests.views import SimpleGetView


class PermissionsDefinitionsTestCase(UtilityTestCase):

    def test_is_authenticated(self):
        request = self.get_request()
        self.assertFalse(AuthenticatedPermissions().check(request))
        request.user = self.user
        self.assertTrue(AuthenticatedPermissions().check(request))

    def test_is_superuser(self):
        request = self.get_request()
        self.assertFalse(AuthenticatedPermissions().check(request))
        request.user = self.admin
        self.assertTrue(AuthenticatedPermissions().check(request))
        self.assertTrue(SuperuserPermissions().check(request))

    def test_is_staff(self):
        request_staff = self.get_request()
        request_admin = self.get_request()
        request_staff.user = self.staff
        request_admin.user = self.admin
        self.assertTrue(StaffPermissions().check(request_staff))
        self.assertFalse(StaffPermissions().check(request_admin))

    def test_staff_or_superuser(self):
        request_staff = self.get_request()
        request_admin = self.get_request()
        request_staff.user = self.staff
        request_admin.user = self.admin
        self.assertTrue(OrStaffSuperuserPermissions().check(request_staff))
        self.assertTrue(OrStaffSuperuserPermissions().check(request_admin))

    def test_staff_and_superuser(self):
        request_staff = self.get_request()
        request_admin = self.get_request()
        request_user = self.get_request()
        request_staff.user = self.staff
        request_admin.user = self.admin
        request_user.user = self.user
        self.assertFalse(AndStaffSuperuserPermissions().check(request_staff))
        self.assertFalse(AndStaffSuperuserPermissions().check(request_admin))
        self.assertFalse(AndStaffSuperuserPermissions().check(request_user))
        self.staff.is_superuser = True
        self.admin.is_staff = True
        self.assertTrue(AndStaffSuperuserPermissions().check(request_staff))
        self.assertTrue(AndStaffSuperuserPermissions().check(request_admin))
        self.assertFalse(AndStaffSuperuserPermissions().check(request_user))

    def test_request_objects(self):
        request_user = self.get_request()
        request_admin = self.get_request()
        request_user.user = self.user
        self.assertFalse(IsPublicPermissions().check(request_user))
        self.assertFalse(IsPublicPermissions().check(request_admin))
        self.assertFalse(AuthenticatedPermissions().check(request_admin))
        self.user.is_public = True
        self.user.save()
        self.assertTrue(IsPublicPermissions().check(request_user))
        self.assertFalse(IsPublicPermissions().check(request_admin))

    def test_negation_request_objects(self):
        request_user = self.get_request()
        request_admin = self.get_request()
        request_user.user = self.user
        request_admin.user = self.admin
        self.assertTrue(AuthenticatedPermissions().check(request_user))
        self.assertTrue(AuthenticatedPermissions().check(request_admin))
        self.assertFalse(NegatePermissions().check(request_user))
        self.assertFalse(NegatePermissions().check(request_admin))
        self.user.is_public = True
        self.user.save()
        self.admin.is_public = True
        self.admin.save()
        self.assertTrue(NegatePermissions().check(request_user))
        self.assertTrue(NegatePermissions().check(request_admin))

    def test_nested_permissions(self):
        request_admin = self.get_request()
        self.assertFalse(NestedPermissions().check(request_admin))
        request_admin.user = self.admin
        self.assertFalse(NestedPermissions().check(request_admin))
        self.admin.username = 'admin2'
        self.assertFalse(NestedPermissions().check(request_admin))
        self.admin.is_staff = True
        self.assertTrue(NestedPermissions().check(request_admin))

    def test_request_params(self):
        request_admin = self.get_request()
        self.assertFalse(RequestParamPermissions().check(request_admin))
        request_admin.user = self.admin
        self.assertTrue(RequestParamPermissions().check(request_admin))

    def test_overrides(self):
        request_admin = self.get_request()
        OverrideIfFalsePermissions().check(request_admin)
        self.assertEqual(OVERRIDE_FALSE, request_admin.permissionsx_return_overrides[0]())
        OverrideIfTrueFalsePermissions().check(request_admin)
        self.assertEqual(OVERRIDE_FALSE, request_admin.permissionsx_return_overrides[0]())
        NegatedOverrideIfTrueFalsePermissions().check(request_admin)
        self.assertEqual(OVERRIDE_FALSE, request_admin.permissionsx_return_overrides[0]())
        NestedNegatedOverridePermissions().check(request_admin)
        self.assertEqual(OVERRIDE_FALSE, request_admin.permissionsx_return_overrides[0]())
        request_admin.user = self.admin
        OverrideIfTruePermissions().check(request_admin)
        self.assertEqual(OVERRIDE_TRUE, request_admin.permissionsx_return_overrides[0]())
        OverrideIfTrueFalsePermissions().check(request_admin)
        self.assertEqual(OVERRIDE_TRUE, request_admin.permissionsx_return_overrides[0]())
        NegatedOverrideIfTrueFalsePermissions().check(request_admin)
        self.assertEqual(OVERRIDE_TRUE, request_admin.permissionsx_return_overrides[0]())
        NestedNegatedOverridePermissions().check(request_admin)
        self.assertEqual(OVERRIDE_TRUE, request_admin.permissionsx_return_overrides[0]())

    def test_oneliners(self):
        request = self.get_request()
        self.assertFalse(
            Permissions(
                P(user__is_authenticated=True) & P(user__username=request.user.username)
            ).check(request)
        )
        request.user = self.user
        self.assertTrue(
            Permissions(
                P(user__is_authenticated=True) | P(user__username='someotheruser')
            ).check(request)
        )
        Permissions(
            user_is_authenticated & P(user__is_superuser=True, if_false=if_true_override)
        ).check(request)
        self.assertEqual(OVERRIDE_TRUE, request.permissionsx_return_overrides[0]())
        Permissions(
            user_is_superuser | P(user__is_staff=True, if_false=if_false_override)
        ).check(request)
        self.assertEqual(OVERRIDE_FALSE, request.permissionsx_return_overrides[0]())
        permissions_tested = Permissions(
            P(user__is_authenticated=True) &
            P(user__is_staff=True, if_false=if_false_override) &
            P(user__is_superuser=False)
        )
        permissions_tested.check(request)
        self.assertEqual(OVERRIDE_FALSE, request.permissionsx_return_overrides[0]())
        request.user = self.staff
        permissions_tested = Permissions(
            P(user__is_authenticated=True) &
            P(user__is_staff=True, if_true=if_true_override) &
            P(user__is_superuser=False)
        )
        permissions_tested.check(request)
        self.assertEqual(OVERRIDE_TRUE, request.permissionsx_return_overrides[0]())

    def test_request_arguments(self):
        request = self.get_request()
        request.user = self.user
        request.user2 = self.admin
        self.assertTrue(
            Permissions(
                P(user__user_is_user=Arg('user'))
            ).check(request)
        )
        self.assertFalse(
            Permissions(
                P(user__user_is_user=Arg('user2'))
            ).check(request)
        )

    def test_nested_negated(self):
        request_admin = self.get_request()
        self.assertFalse(NestedNegatedPermissions().check(request_admin))
        request_admin.user = self.admin
        self.assertTrue(NestedNegatedPermissions().check(request_admin))

    def test_children(self):
        self.assertEqual(
            '(&(&(~(&{\'user\': 1})),(|{\'user\': 2},(~(&{\'user\': 3})))))',
            str(P(~P(user=1) & P(P(user=2) | ~P(user=3))))
        )


class PermissionsDjangoViewsTestCase(UtilityTestCase):

    def setUp(self):
        super(PermissionsDjangoViewsTestCase, self).setUp()
        self.test_object = TestObject.objects.create(title='Test!')

    def test_authenticated(self):
        response = self.client.get(reverse('authenticated'), follow=True)
        self.assertContains(response, 'Login')
        self.login(self.client, 'user')
        response = self.client.get(reverse('authenticated'), follow=True)
        self.assertContains(response, 'Passed')

    @mock.patch('permissionsx.settings.LOGOUT_IF_DENIED', True)
    def test_settings_logout(self):
        self.login(self.client, 'user')
        self.assertTrue(auth.get_user(self.client).is_authenticated())
        response = self.client.get(reverse('authenticated'), follow=True)
        self.assertContains(response, 'Passed')
        response = self.client.get(reverse('authenticated'), follow=True)
        self.assertContains(response, 'Passed')
        response = self.client.get(reverse('superuser'), follow=True)
        self.assertFalse(auth.get_user(self.client).is_authenticated())

    @mock.patch('permissionsx.settings.REDIRECT_URL', '/accounts/login2/')
    def test_settings_redirect_url(self):
        response = self.client.get(reverse('authenticated'), follow=True)
        self.assertContains(response, 'Login2')

    def test_no_redirect_if_authenticated(self):
        request = self.get_request()
        redirect_url = RedirectView(
            request=request,
            redirect_url='/redirected/',
        ).get_redirect_url()
        self.assertEqual(redirect_url, '/redirected/?next=/')
        request.user = self.user
        redirect_url = RedirectView(
            request=request,
            redirect_url='/redirected/',
        ).get_redirect_url()
        self.assertEqual(redirect_url, '/redirected/')

    def test_response_class(self):
        response = self.client.get(reverse('response_class'), follow=True)
        self.assertContains(response, 'Access Denied')
        self.assertContains(response, 'Login')

    def test_if_false_override(self):
        self.login(self.client, 'user')
        response = self.client.get(reverse('overrides_if_false'), follow=True)
        self.assertContains(response, 'Login2')

    def test_if_true_override(self):
        response = self.client.get(reverse('overrides_if_true'), follow=True)
        self.assertContains(response, 'Login')
        self.login(self.client, 'user')
        response = self.client.get(reverse('overrides_if_true'), follow=True)
        self.assertContains(response, 'Passed')
        self.login(self.client, 'admin')
        response = self.client.get(reverse('overrides_if_true'), follow=True)
        self.assertContains(response, 'Welcome')

    def test_both_overrides(self):
        response = self.client.get(reverse('overrides_both'), follow=True)
        self.assertContains(response, 'Login2')
        self.login(self.client, 'user')
        response = self.client.get(reverse('overrides_both'), follow=True)
        self.assertContains(response, 'Passed')
        self.login(self.client, 'admin')
        response = self.client.get(reverse('overrides_both'), follow=True)
        self.assertContains(response, 'Welcome')

    def test_subsequent_overrides(self):
        response = self.client.get(reverse('subsequent_overrides'), follow=True)
        self.assertContains(response, 'Login2')
        self.login(self.client, 'user')
        response = self.client.get(reverse('subsequent_overrides'), follow=True)
        self.assertContains(response, 'Welcome')

    def test_template_tag(self):
        response = self.client.get(reverse('menu'), follow=True)
        self.assertContains(response, 'Login')
        self.login(self.client, 'user')
        response = self.client.get(reverse('menu'), follow=True)
        self.assertContains(response, 'User Menu')
        self.login(self.client, 'staff')
        response = self.client.get(reverse('menu'), follow=True)
        self.assertContains(response, 'Staff Menu')

    def test_template_tag_permissions_for_user_attrs_anonymous(self):
        self.user.username = 'user_username'
        context = {'request': self.get_request()}
        self.assertFalse(
            permissions(
                context,
                'permissionsx.tests.permissions.UserAttributesDependentPermissions'
            )
        )

    def test_template_tag_permissions_for_user_attrs_no_request(self):
        from django.contrib.auth.models import AnonymousUser
        self.user.username = 'user_username'
        context = {'user': AnonymousUser()}
        self.assertFalse(
            permissions(
                context,
                'permissionsx.tests.permissions.UserAttributesDependentPermissions'
            )
        )

    def test_template_tag_permissions_for_user_attrs_authenticated(self):
        request = self.get_request()
        request.user = self.user
        context = {'request': request}
        self.assertFalse(
            permissions(
                context,
                'permissionsx.tests.permissions.UserAttributesDependentPermissions'
            )
        )

        self.user.username = 'user_username'
        request = self.get_request()
        request.user = self.user
        context = {'request': request}
        self.assertTrue(
            permissions(
                context,
                'permissionsx.tests.permissions.UserAttributesDependentPermissions'
            )
        )

    def test_combining_permissions(self):

        class SomeBasicObjectPermissions(Permissions):

            rules = P(some_object1__title='Some Object 1')

            def get_rules(self, request, **kwargs):
                request.some_object1 = TestObject(title='Some Object 1')
                request.some_object2 = TestObject(title='Some Object 2')
                request.some_object3 = TestObject(title='Some Object 3')
                return P(some_object2__title='Some Object 2')

        class SomeObjectPermissions(SomeBasicObjectPermissions):

            def get_rules(self, request, **kwargs):
                rules = super(SomeObjectPermissions, self).get_rules(request, **kwargs)
                request.some_object4 = TestObject(title='Some Object 4')
                return rules & P(some_object3__title='Some Object 3')

        class TestView(DjangoViewMixin, SimpleGetView):

            permissions = SomeObjectPermissions(
                P(some_object4__title='Some Object 4')
            )

        request = self.factory.get('/')
        combined_rules = TestView.permissions.get_combined_rules(request)
        self.assertEqual(
            str(combined_rules),
            '(&{\'some_object1__title\': \'Some Object 1\'},'
            '{\'some_object4__title\': \'Some Object 4\'},'
            '{\'some_object2__title\': \'Some Object 2\'},'
            '{\'some_object3__title\': \'Some Object 3\'})'
        )

    def test_combining_permissions_with_none(self):

        class SomeObjectPermissions(Permissions):

            # NOTE: Inherits `permissions == None` from Permissions.
            def get_rules(self, request, **kwargs):
                request.some_object = TestObject(title='Some Object')

        class TestView(DjangoViewMixin, SimpleGetView):

            permissions = SomeObjectPermissions(
                P(user_is_staff | user_is_superuser)
            )

        request = self.factory.get('/')
        response = TestView().dispatch(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.some_object.title, 'Some Object')

    def test_exception_raised_when_no_permissions(self):

        class TestView(DjangoViewMixin, SimpleGetView):
            pass

        request = self.factory.get('/')
        self.assertRaises(ImproperlyConfigured, TestView().dispatch, request)


class DjangoDebugToolbarIntegrationTestCase(UtilityTestCase):

    @override_settings(SHOW_TOOLBAR=True)
    def test_django_debug_toolbar_rendered(self):
        response = self.client.get(reverse('authenticated'), follow=True)
        self.assertContains(response, 'permissionsx.tests.views.LoginView')
        self.login(self.client, 'user')
        response = self.client.get(reverse('authenticated'), follow=True)
        self.assertContains(
            response,
            'permissionsx.tests.permissions.AuthenticatedPermissions'
        )
        self.assertContains(
            response,
            'user__is_authenticated'
        )


class DjangoTastypieIntegrationTestCase(UtilityTestCase):

    def setUp(self):
        super(DjangoTastypieIntegrationTestCase, self).setUp()
        self.test_object = TestObject.objects.create(title='Test!')

    def test_tastypie_authorization_general(self):
        response = self.client.get('/api/v1/testsuperuser/1/')
        self.assertEqual(response.status_code, 401)
        self.login(self.client, 'user')
        response = self.client.get('/api/v1/testsuperuser/1/')
        self.assertEqual(response.status_code, 401)
        self.login(self.client, 'admin')
        response = self.client.get('/api/v1/testsuperuser/1/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test!')

    def test_tastypie_authorization_overrides(self):
        json_data = json.dumps({'title': 'Changed!'})
        response = self.client.put(
            '/api/v1/testoverride/1/',
            json_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        self.login(self.client, 'user')
        response = self.client.put(
            '/api/v1/testoverride/1/',
            json_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(TestObject.objects.get(id=1).title, 'Changed!')
