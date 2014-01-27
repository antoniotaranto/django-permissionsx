========
Settings
========

PERMISSIONSX_REDIRECT_URL
=========================

Defaults to `settings.LOGIN_URL`.

If user has not been granted permission to access a Django view, redirect to `PERMISSIONSX_REDIRECT_URL`.

PERMISSIONSX_LOGOUT_IF_DENIED
=============================

Defaults to `False`.

If user has not been granted permission to access a Django view, log the user out before redirecting to `PERMISSIONSX_REDIRECT_URL`.
