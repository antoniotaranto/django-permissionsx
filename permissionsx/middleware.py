"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.conf import settings as django_settings
from django.core.exceptions import (
    ImproperlyConfigured,
    ObjectDoesNotExist,
    )

from permissionsx import settings
from permissionsx.utils import get_class


class PermissionsXProfileMiddleware(object):

    def process_request(self, request):
        assert hasattr(request, 'user'), 'PermissionsXProfileMiddleware requires AuthenticationMiddleware to be installed.'
        if django_settings.AUTH_PROFILE_MODULE:
            # NOTE: Using 1-1 profiles, attach anonymous one.
            try:
                request.profile = request.user.get_profile()
            except (TypeError, AttributeError, ObjectDoesNotExist):
                request.profile = AnonymousProfile()


if filter(lambda m:'PermissionsXProfileMiddleware' in m, django_settings.MIDDLEWARE_CLASSES):
    """ This is mostly for compatibility with Django 1.4. If using > Django 1.5, you are more likely be using
    custom user models.

    """
    if django_settings.AUTH_PROFILE_MODULE:
        anonymous_profile_cls = getattr(settings, 'PERMISSIONSX_ANONYMOUS_PROFILE')
        try:
            module, _, name = anonymous_profile_cls.rpartition('.')
            AnonymousProfile = get_class(module, name)
        except ImportError:
            raise ImproperlyConfigured('"{}" is invalid setting value for PERMISSIONSX_ANONYMOUS_PROFILE'.format(anonymous_profile_cls))
