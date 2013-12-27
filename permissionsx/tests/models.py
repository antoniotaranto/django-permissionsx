"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.db import models


class Profile(models.Model):

    user = models.ForeignKey('auth.User')
    is_public = models.BooleanField(default=False)

    def is_attached_to_user(self, user):
        return self.user == user


class AnonymousProfile(object):

    user = None
    is_public = False

    def is_attached_to_user(self, user):
        return False


class TestObject(models.Model):

    title = models.CharField(max_length=50)
