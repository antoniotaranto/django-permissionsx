=========
Changelog
=========

1.1.2
=====

* Added support over overriding response behavior on a permission level.
* One-liners for defining permissions.
* :class:`Arg` allows passing request object to permission checking function.
* Package :mod:`django-classy-tags` is no longer a requirement.
* Added Sphinx documentation with extended examples.

1.1.0
=====

* New syntax possible for retrieving related objects, e.g. ``P(user__get_profile__related_object__is_something=True)``.

1.0.0
=====

* Added support for custom response classes (e.g. for changing redirect URL, adding custom user message).
* Added tests for checking permissions.
* Minor fixes and improvements.

0.0.9
=====

* Added support for Django templates, including per-object checks.
* Renamed class-level :attr:`permissions` to :attr:`permissions_class`.
* Dropped support for simple permissions defining for the benefit of greater flexibility.
* Renaming and refactoring, again. Good stuff: managed to get rid of middleware and a class. Things got largely simplified in general.
* Requirement: :mod:`django-classy-tags`.

0.0.8
=====

* This version is backward **incompatible**.
* Changed syntax to follow QuerySet filtering convention.
* Sadly, tests are gone. Need to write new ones, what will not happen until 1.0.0 release.
* Example project's gone. Will be back at a different URL.
* :attr:`PERMISSIONSX_DEFAULT_URL` was renamed to :attr:`PERMISSIONSX_REDIRECT_URL`.
* New setting was added: :attr:`PERMISSIONSX_LOGOUT_IF_DENIED`.

