"""
PermissionsX - Authorization for Django Class-Based Views.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
class CustomActor(object):

    def __init__(self, user):
        self.user = user

    def doesnt_own(self, something):
        return bool(something.owned_by(self.user))


class Something(object):

    def __init__(self, username, active=True):
        self.username = username
        self.active = active

    def is_active(self):
        return self.active

    def owned_by(self, user):
        return self.username == user.username


somethings = {
    '1': Something('user'), # NOTE: "user" owns object with pk == "1".
    '2': Something('user-b'), # NOTE: "user-b" owns object with pk == "2".
    '3': Something('user', active=False), # NOTE: "user" owns object with pk == "3" which is NOT active.
}
