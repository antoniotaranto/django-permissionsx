===============
Important Notes
===============

Django Views
============

* If an anonymous user is being redirected, current ``request.get_full_path()`` will be added to the URL as `next` parameter.
* Overrides for Django views must accept ``(request, *args, **kwargs)``.
