"""
PermissionsX - Authorization for Django Class-Based Views.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from permissionsx.utils import get_class


class PermissionsXProfileMiddleware(object):

    def process_request(self, request):
        assert hasattr(request, 'user'), 'PermissionsXProfileMiddleware requires AuthenticationMiddleware to be installed.'
        try:        
            request.profile = request.user.get_profile()
        except (TypeError, AttributeError):
            request.profile = AnonymousActor()


if filter(lambda m:'PermissionsXProfileMiddleware' in m, settings.MIDDLEWARE_CLASSES):
    anonymous_cls = getattr(settings, 'PERMISSIONS_ANONYMOUS_ACTOR', None)
    if anonymous_cls is None:
        raise ImproperlyConfigured('PERMISSIONS_ANONYMOUS_ACTOR setting is missing')
    try:
        AnonymousActor = get_class(anonymous_cls)
    except ImportError:
        raise ImproperlyConfigured('"{}" is invalid setting value for PERMISSIONS_ANONYMOUS_ACTOR'.format(anonymous_cls))