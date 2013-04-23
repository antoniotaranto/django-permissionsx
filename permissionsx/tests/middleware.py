"""
PermissionsX - Authorization for Django Class-Based Views.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from permissionsx.tests.models import CustomActor


class PermissionsCustomRequestObjectMiddleware(object):

    def process_request(self, request):
        request.custom_actor = CustomActor(request.user)
