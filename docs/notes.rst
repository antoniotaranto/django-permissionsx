===============
Important Notes
===============

Django Views
============

* If an anonymous user is being redirected, current ``request.get_full_path()`` will be added to the URL as `next` parameter.
* Overrides for Django views must accept ``(request, *args, **kwargs)``.

Caching
=======

* You won't need caching if there are no intense database queries on each request. For performing checks on request objects and anything related turning cache on might actually slow things down.
* It looks that the only reasonable way of caching permissions is in-memory and per instance. Anything else is just too much overhead, including distributed Redis and Django LocMem.
* Cache prefixes are based on ``User.pk``.