"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import


class DummyRequest(object):
    """This class is used internally with Django templates to isolate permission
    checks from original :class:`HttpRequest` context.

    """
    user = None

    def __init__(self, user=None):
        if user is not None:
            self.user = user
