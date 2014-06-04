"""PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

from django.conf import settings


REDIRECT_URL = getattr(settings, 'PERMISSIONSX_REDIRECT_URL', settings.LOGIN_URL)
LOGOUT_IF_DENIED = getattr(settings, 'PERMISSIONSX_LOGOUT_IF_DENIED', False)
