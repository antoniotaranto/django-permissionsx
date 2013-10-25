"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
__all__ = ['permissions_cache']


class SimpleCache(object):

    def __init__(self):
        self._cache = {}

    def get_key(self, request, key):
        if hasattr(request, 'user'):
            user_key = str(request.user.pk)
        else:
            user_key = '?'
        return user_key + ':' + str(key)

    def get(self, request, key):
        try:
            return self._cache[self.get_key(request, key)]
        except KeyError:
            return None

    def set(self, request, key, value):
        self._cache[self.get_key(request, key)] = value

    def delete(self, request, key):
        try:
            del self._cache[self.get_key(request, key)]
        except KeyError:
            pass


class PermissionsCache(SimpleCache):

    def set_cache(self, request, cache_key, result):
        user_key, _, _ = cache_key.partition(':')
        user_key_list = self.get(request, user_key) or []
        if cache_key not in user_key_list:
            user_key_list.append(cache_key)
        self.set(request, user_key, user_key_list)
        self.set(request, cache_key, result)

    def get_cache(self, request, cache_key):
        result = self.get(request, cache_key)
        if result is None:
            return None, None
        return result

    def invalidate_user_cache(self, request, user_key):
        user_key_list = self.get(request, user_key)
        if user_key_list:
            for key in user_key_list:
                self.delete(request, key)
        self.delete(request, user_key)


permissions_cache = PermissionsCache()
