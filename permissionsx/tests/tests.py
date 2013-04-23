import os

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from permissionsx.tests.views import (
    OK_RESPONSE,
    LOGIN_RESPONSE,
)


class PermissionsXTests(TestCase):
    
    urls = 'permissionsx.tests.urls'
    
    def setUp(self):
        self.user = User.objects.create_user('user', 'user@example.com', 'password')

    def test_login_required(self):
        c = Client()
        response = c.get(reverse('is_authenticated'))
        self.assertEqual(response.status_code, 403)
        c.login(username='user', password='password')
        response = c.get(reverse('is_authenticated'))
        self.assertEqual(response.status_code, 200)

    def test_login_required_redirect(self):
        c = Client()
        response = c.get(reverse('is_authenticated_redirect'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, LOGIN_RESPONSE)

    def test_anonymous(self):
        c = Client()
        response = c.get(reverse('anonymous'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, OK_RESPONSE)

    def test_request_context(self):
        c = Client()
        response = c.get(reverse('request_context', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)
        c.login(username='user', password='password')
        response = c.get(reverse('request_context', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('request_context', kwargs={'pk': 2}))
        self.assertEqual(response.status_code, 403)

    def test_request_context_redirect(self):
        c = Client()
        response = c.get(reverse('request_context_redirect', kwargs={'pk': 1}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, LOGIN_RESPONSE)
        c.login(username='user', password='password')
        response = c.get(reverse('request_context_redirect', kwargs={'pk': 1}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, LOGIN_RESPONSE)
        response = c.get(reverse('request_context_redirect', kwargs={'pk': 2}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, LOGIN_RESPONSE)

    def test_request_context_redirect_authenticated(self):
        c = Client()
        response = c.get(reverse('request_context_redirect_authenticated', kwargs={'pk': 1}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, LOGIN_RESPONSE)
        c.login(username='user', password='password')
        response = c.get(reverse('request_context_redirect_authenticated', kwargs={'pk': 1}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, LOGIN_RESPONSE)
        response = c.get(reverse('request_context_redirect_authenticated', kwargs={'pk': 2}), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_request_context_attribute_check(self):
        c = Client()
        c.login(username='user', password='password')
        response = c.get(reverse('request_context_attribute_check', kwargs={'pk': 1}), follow=True)
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('request_context_attribute_check', kwargs={'pk': 3}), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_multiple_or_check(self):
        # NOTE: is_staff == True, is_superuser == False
        userA = User.objects.create_user('user-a', 'user.a@example.com', 'password')
        userA.is_staff = True
        userA.save()
        # NOTE: is_staff == False, is_superuser == True
        userB = User.objects.create_user('user-b', 'user.b@example.com', 'password')
        userB.is_superuser = True
        userB.save()
        # NOTE: is_staff == True, is_superuser == True
        userC = User.objects.create_user('user-c', 'user.c@example.com', 'password')
        userC.is_staff = True
        userC.is_superuser = True
        userC.save()
        # NOTE: is_staff == False, is_superuser == False
        userD = User.objects.create_user('user-d', 'user.d@example.com', 'password')

        c = Client()

        # NOTE: Test anonymous.
        response = c.get(reverse('or_permissions'), follow=True)
        self.assertEqual(response.status_code, 403)
        response = c.get(reverse('or_permissions_redirect'), follow=True)
        self.assertEqual(response.status_code, 403)
        response = c.get(reverse('or_permissions_ya_redirect'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, LOGIN_RESPONSE)
        response = c.get(reverse('or_permissions_ya_2_redirect'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, LOGIN_RESPONSE)

        # NOTE: Test user__is_staff == False and user__is_superuser == False.
        c.login(username='user-d', password='password')
        response = c.get(reverse('or_permissions'), follow=True)
        self.assertEqual(response.status_code, 403)
        response = c.get(reverse('or_permissions_redirect'), follow=True)
        self.assertEqual(response.status_code, 403)
        response = c.get(reverse('or_permissions_ya_redirect'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, LOGIN_RESPONSE)
        response = c.get(reverse('or_permissions_ya_2_redirect'), follow=True)
        self.assertEqual(response.status_code, 403)

        # NOTE: Test user__is_staff == True and user__is_superuser == True.
        c.login(username='user-c', password='password')
        response = c.get(reverse('or_permissions'), follow=True)
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('or_permissions_redirect'), follow=True)
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('or_permissions_ya_redirect'), follow=True)
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('or_permissions_ya_2_redirect'), follow=True)
        self.assertEqual(response.status_code, 200)

        # NOTE: Test user__is_staff == False and user__is_superuser == True.
        c.login(username='user-b', password='password')
        response = c.get(reverse('or_permissions'), follow=True)
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('or_permissions_redirect'), follow=True)
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('or_permissions_ya_redirect'), follow=True)
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('or_permissions_ya_2_redirect'), follow=True)
        self.assertEqual(response.status_code, 200)

        # NOTE: Test user__is_staff == True and user__is_superuser == False.
        c.login(username='user-a', password='password')
        response = c.get(reverse('or_permissions'), follow=True)
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('or_permissions_redirect'), follow=True)
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('or_permissions_ya_redirect'), follow=True)
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('or_permissions_ya_2_redirect'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_request_context_custom_middleware(self):
        userB = User.objects.create_user('user-b', 'user.b@example.com', 'password')
        c = Client()
        c.login(username='user-b', password='password')
        response = c.get(reverse('request_context_custom_middleware', kwargs={'pk': 2}), follow=True)
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('request_context_custom_middleware', kwargs={'pk': 3}), follow=True)
        self.assertEqual(response.status_code, 403)
