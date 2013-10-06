"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.db import models


class Profile(models.Model):

    user = models.ForeignKey('auth.User')
    is_public = models.BooleanField()


class AnonymousProfile(object):

    user = None
    is_public = False