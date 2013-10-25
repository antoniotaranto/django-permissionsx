"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.core.urlresolvers import reverse
from django.contrib.auth import login

from permissionsx.tests.test_utils import UtilityTestCase
from permissionsx.tests.test_utils import SettingsOverride
from permissionsx.models import Arg
from permissionsx.tests.permissions import *
from permissionsx.tests.models import TestObject


class PermissionsDefinitionsTests(UtilityTestCase):

    def test_is_authenticated(self):
        request = self.get_request_for_user(self.user)
        self.assertFalse(self.permissions_for_request(AuthenticatedPermissions, request))
        login(request, self.user)
        self.assertTrue(self.permissions_for_request(AuthenticatedPermissions, request))

    def test_is_superuser(self):
        request = self.get_request_for_user(self.admin)
        self.assertFalse(self.permissions_for_request(AuthenticatedPermissions, request))
        login(request, self.admin)
        self.assertTrue(self.permissions_for_request(AuthenticatedPermissions, request))
        self.assertTrue(self.permissions_for_request(SuperuserPermissions, request))

    def test_is_staff(self):
        request_staff = self.get_request_for_user(self.staff)
        request_admin = self.get_request_for_user(self.admin)
        login(request_staff, self.staff)
        login(request_admin, self.admin)
        self.assertTrue(self.permissions_for_request(StaffPermissions, request_staff))
        self.assertFalse(self.permissions_for_request(StaffPermissions, request_admin))

    def test_staff_or_superuser(self):
        request_staff = self.get_request_for_user(self.staff)
        request_admin = self.get_request_for_user(self.admin)
        login(request_staff, self.staff)
        login(request_admin, self.admin)
        self.assertTrue(self.permissions_for_request(OrStaffSuperuserPermissions, request_staff))
        self.assertTrue(self.permissions_for_request(OrStaffSuperuserPermissions, request_admin))

    def test_staff_and_superuser(self):
        request_staff = self.get_request_for_user(self.staff)
        request_admin = self.get_request_for_user(self.admin)
        request_user = self.get_request_for_user(self.user)
        login(request_staff, self.staff)
        login(request_admin, self.admin)
        login(request_user, self.user)
        self.assertFalse(self.permissions_for_request(AndStaffSuperuserPermissions, request_staff))
        self.assertFalse(self.permissions_for_request(AndStaffSuperuserPermissions, request_admin))
        self.assertFalse(self.permissions_for_request(AndStaffSuperuserPermissions, request_user))
        self.staff.is_superuser = True
        self.admin.is_staff = True
        # NOTE: User must log in again if permissions changed - cleaning
        #       cache for a specific user.
        login(request_staff, self.staff)
        login(request_admin, self.admin)
        self.assertTrue(self.permissions_for_request(AndStaffSuperuserPermissions, request_staff))
        self.assertTrue(self.permissions_for_request(AndStaffSuperuserPermissions, request_admin))
        self.assertFalse(self.permissions_for_request(AndStaffSuperuserPermissions, request_user))

    def test_request_objects(self):
        request_user = self.get_request_for_user(self.user)
        request_admin = self.get_request_for_user(self.admin)
        login(request_user, self.user)
        self.assertFalse(self.permissions_for_request(IsPublicPermissions, request_user))
        self.assertFalse(self.permissions_for_request(IsPublicPermissions, request_admin))
        self.assertFalse(self.permissions_for_request(AuthenticatedPermissions, request_admin))
        self.user.get_profile().is_public = True
        login(request_user, self.user)
        self.assertTrue(self.permissions_for_request(IsPublicPermissions, request_user))
        self.assertFalse(self.permissions_for_request(IsPublicPermissions, request_admin))

    def test_negation_request_objects(self):
        request_user = self.get_request_for_user(self.user)
        request_admin = self.get_request_for_user(self.admin)
        login(request_user, self.user)
        login(request_admin, self.admin)
        self.assertTrue(self.permissions_for_request(AuthenticatedPermissions, request_user))
        self.assertTrue(self.permissions_for_request(AuthenticatedPermissions, request_admin))
        self.assertFalse(self.permissions_for_request(NegatePermissions, request_user))
        self.assertFalse(self.permissions_for_request(NegatePermissions, request_admin))
        self.user.get_profile().is_public = True
        self.admin.get_profile().is_public = True
        login(request_user, self.user)
        login(request_admin, self.admin)
        self.assertTrue(self.permissions_for_request(NegatePermissions, request_user))
        self.assertTrue(self.permissions_for_request(NegatePermissions, request_admin))

    def test_nested_permissions(self):
        request_admin = self.get_request_for_user(self.admin)
        self.assertFalse(self.permissions_for_request(NestedPermissions, request_admin))
        login(request_admin, self.admin)
        self.assertFalse(self.permissions_for_request(NestedPermissions, request_admin))
        self.admin.username = 'admin2'
        login(request_admin, self.admin)
        self.assertFalse(self.permissions_for_request(NestedPermissions, request_admin))
        self.admin.is_staff = True
        login(request_admin, self.admin)
        self.assertTrue(self.permissions_for_request(NestedPermissions, request_admin))

    def test_request_params(self):
        request_admin = self.get_request_for_user(self.admin)
        self.assertFalse(self.permissions_for_request(RequestParamPermissions, request_admin))
        login(request_admin, self.admin)
        self.assertTrue(self.permissions_for_request(RequestParamPermissions, request_admin))

    def test_overrides(self):
        request_admin = self.get_request_for_user(self.admin)
        self.permissions_for_request(OverrideIfFalsePermissions, request_admin)
        self.assertEqual(OVERRIDE_FALSE, request_admin.permissionsx_return_overrides[0]())
        self.permissions_for_request(OverrideIfTrueFalsePermissions, request_admin)
        self.assertEqual(OVERRIDE_FALSE, request_admin.permissionsx_return_overrides[0]())
        self.permissions_for_request(NegatedOverrideIfTrueFalsePermissions, request_admin)
        self.assertEqual(OVERRIDE_FALSE, request_admin.permissionsx_return_overrides[0]())
        self.permissions_for_request(NestedNegatedOverridePermissions, request_admin)
        self.assertEqual(OVERRIDE_FALSE, request_admin.permissionsx_return_overrides[0]())
        login(request_admin, self.admin)
        self.permissions_for_request(OverrideIfTruePermissions, request_admin)
        self.assertEqual(OVERRIDE_TRUE, request_admin.permissionsx_return_overrides[0]())
        self.permissions_for_request(OverrideIfTrueFalsePermissions, request_admin)
        self.assertEqual(OVERRIDE_TRUE, request_admin.permissionsx_return_overrides[0]())
        self.permissions_for_request(NegatedOverrideIfTrueFalsePermissions, request_admin)
        self.assertEqual(OVERRIDE_TRUE, request_admin.permissionsx_return_overrides[0]())
        self.permissions_for_request(NestedNegatedOverridePermissions, request_admin)
        self.assertEqual(OVERRIDE_TRUE, request_admin.permissionsx_return_overrides[0]())

    def test_oneliners(self):
        request = self.get_request_for_user(self.user)
        self.assertFalse(self.permissions_for_request(Permissions(P(user__is_authenticated=True) & P(user__username=request.user.username)), request))
        login(request, self.user)
        self.assertTrue(self.permissions_for_request(Permissions(P(user__is_authenticated=True) | P(user__username='someotheruser')), request))
        self.permissions_for_request(Permissions(user_is_authenticated & P(user__is_superuser=True, if_false=if_true_override)), request)
        self.assertEqual(OVERRIDE_TRUE, request.permissionsx_return_overrides[0]())
        self.permissions_for_request(Permissions(user_is_superuser | P(user__is_staff=True, if_false=if_false_override)), request)
        self.assertEqual(OVERRIDE_FALSE, request.permissionsx_return_overrides[0]())
        permissions_tested = Permissions(
            P(user__is_authenticated=True) &
            P(user__is_staff=True, if_false=if_false_override) &
            P(user__is_superuser=False)
        )
        self.permissions_for_request(permissions_tested, request)
        self.assertEqual(OVERRIDE_FALSE, request.permissionsx_return_overrides[0]())
        login(request, self.staff)
        permissions_tested = Permissions(
            P(user__is_authenticated=True) &
            P(user__is_staff=True, if_true=if_true_override) &
            P(user__is_superuser=False)
        )
        self.permissions_for_request(permissions_tested, request)
        self.assertEqual(OVERRIDE_TRUE, request.permissionsx_return_overrides[0]())

    def test_request_arguments(self):
        request = self.get_request_for_user(self.user)
        setattr(request, 'user2', self.admin)
        login(request, self.user)
        self.assertTrue(self.permissions_for_request(Permissions(P(user__get_profile__is_attached_to_user=Arg('user'))), request))
        self.assertFalse(self.permissions_for_request(Permissions(P(user__get_profile__is_attached_to_user=Arg('user2'))), request))

    def test_nested_negated(self):
        request_admin = self.get_request_for_user(self.admin)
        self.assertFalse(self.permissions_for_request(NestedNegatedPermissions, request_admin))
        login(request_admin, self.admin)
        self.assertTrue(self.permissions_for_request(NestedNegatedPermissions, request_admin))

    def test_children(self):
        self.assertEqual(
            '(&(&(~(&{\'user\': 1})),(|{\'user\': 2},(~(&{\'user\': 3})))))',
            str(P(~P(user=1) & P(P(user=2) | ~P(user=3))))
        )


class PermissionsDjangoViews(UtilityTestCase):

    def setUp(self):
        super(PermissionsDjangoViews, self).setUp()
        self.test_object = TestObject.objects.create(title='Test!')

    def test_authenticated(self):
        response = self.client.get(reverse('authenticated'), follow=True)
        self.assertContains(response, 'Login')
        self.login(self.client, 'user')
        response = self.client.get(reverse('authenticated'), follow=True)
        self.assertContains(response, 'Passed')

    def test_get_profile(self):
        # NOTE: Uses OrStaffSuperuserPermissions == P(user__is_staff=True) | P(user__is_administrator=True)
        response = self.client.get(reverse('get_profile'), follow=True)
        self.assertContains(response, 'Login')
        self.login(self.client, 'user')
        self.assertContains(response, 'Login')
        self.login(self.client, 'staff')
        response = self.client.get(reverse('get_profile'), follow=True)
        self.assertContains(response, 'Passed')
        self.login(self.client, 'admin')
        response = self.client.get(reverse('get_profile'), follow=True)
        self.assertContains(response, 'Passed')

    def test_settings_logout(self):
        with SettingsOverride(PERMISSIONSX_LOGOUT_IF_DENIED=True):
            self.login(self.client, 'user')
            response = self.client.get(reverse('authenticated'), follow=True)
            self.assertContains(response, 'Passed')
            self.client.get(reverse('superuser'), follow=True)
            self.assertNotIn('_auth_user_id', self.client.session)

    def test_settings_redirect_url(self):
        with SettingsOverride(PERMISSIONSX_REDIRECT_URL='/accounts/login2/'):
            response = self.client.get(reverse('authenticated'), follow=True)
            self.assertContains(response, 'Login2')

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
