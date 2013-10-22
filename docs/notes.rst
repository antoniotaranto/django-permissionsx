===============
Important Notes
===============

* If a user is being redirected while not being logged in (``request.user.is_authenticated()``), current ``request.get_full_path()`` will be added to the URL as `next` parameter.
* Overrides for Django views must accept ``(request, *args, **kwargs)``.
