"""
PermissionsX - Authorization for Django Class-Based Views.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from permissionsx.tests.models import Actor


class PermissionsXTestActorMiddleware(object):
    """Adds Actor mock for use with permissionsx."""
    
    def process_request(self, request):
        assert hasattr(request, 'user'), 'PermissionsXTestActorMiddleware requires AuthenticationMiddleware to be installed.'
        request.actor = Actor(request.user)
