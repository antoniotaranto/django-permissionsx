"""PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

from django.db import models
from django.contrib.auth.models import AbstractUser


class Profile(AbstractUser):

    is_public = models.BooleanField(default=False)

    def user_is_user(self, user):
        return self == user


class TestObject(models.Model):

    title = models.CharField(max_length=50)
    owner = models.ForeignKey(Profile)
