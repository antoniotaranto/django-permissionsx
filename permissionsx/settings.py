"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.conf import settings


PERMISSIONSX_REDIRECT_URL = getattr(settings, 'PERMISSIONSX_REDIRECT_URL', settings.LOGIN_URL)
PERMISSIONSX_LOGOUT_IF_DENIED = getattr(settings, 'PERMISSIONSX_LOGOUT_IF_DENIED', False)
PERMISSIONSX_DEBUG = getattr(settings, 'PERMISSIONSX_DEBUG', False)
