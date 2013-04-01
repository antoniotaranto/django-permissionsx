import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings

from permissionsx.tests.views import (
    OK_RESPONSE,
    LOGIN_RESPONSE,
)


@override_settings(
    MIDDLEWARE_CLASSES=(
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'permissionsx.middleware.PermissionsXMiddleware',
        'permissionsx.tests.middleware.PermissionsXTestActorMiddleware',
    ),
    TEMPLATE_DIRS=(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates'),
    ),
)
class PermissionsXTests(TestCase):
    
    urls = 'permissionsx.tests.urls'
    
    def setUp(self):
        self.user = User.objects.create_user('user-a', 'user.a@example.com', 'password')

    def test_login_required(self):
        c = Client()
        response = c.get(reverse('is_authenticated'))
        self.assertEqual(response.status_code, 403)
        c.login(username='user-a', password='password')
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
        c.login(username='user-a', password='password')
        response = c.get(reverse('request_context', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('request_context', kwargs={'pk': 2}))
        self.assertEqual(response.status_code, 403)

    def test_request_context_redirect(self):
        c = Client()
        response = c.get(reverse('request_context_redirect', kwargs={'pk': 1}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, LOGIN_RESPONSE)
        c.login(username='user-a', password='password')
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
        c.login(username='user-a', password='password')
        response = c.get(reverse('request_context_redirect_authenticated', kwargs={'pk': 1}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, LOGIN_RESPONSE)
        response = c.get(reverse('request_context_redirect_authenticated', kwargs={'pk': 2}), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_request_context_attribute_check(self):
        c = Client()
        c.login(username='user-a', password='password')
        response = c.get(reverse('request_context_attribute_check', kwargs={'pk': 1}), follow=True)
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('request_context_attribute_check', kwargs={'pk': 3}), follow=True)
        self.assertEqual(response.status_code, 403)
