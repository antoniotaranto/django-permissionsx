=========
Changelog
=========

1.3.3
=====

* Minor maintenance release. No changes affecting current installations.

1.3.2
=====

* Minor maintenance release. No changes affecting current installations.
* Changed policy on compatibility. Each release is now guaranteed to support:
 * latest stable release and next upcoming of Django;
 * latest Python 2.x and 3.x versions;
 * latest stable versions of interoperable packages (currently `django-debug-toolbar` and `django-tastypie`)

1.3.1
=====

* Minor maintenance release. No changes affecting current installations.

1.3.0
=====

* On a view level `permissions_class` is now `permissions`.
* Renamed `get_permissions` to `get_rules`.
* Renamed `permissions` to `rules`.
* Renamed `check_permissions` to `check`.
* Other internal API changes.
* Object passed to `permissions` must be an instance.
* Added example project at `<http://github.com/thinkingpotato/django-permissionsx-example>`_.
* Removed `PERMISSIONSX_DEBUG` setting.
* Renamed `PermissionsDebugPanel` to `PermissionsPanel` (following django-debug-toolbar).

1.2.1
=====

* Bugfix release. Merging permissions with a :class:`Permissions` instance with no rules defined was raising `TypeError` exception.

1.2.0
=====

* Removed `set_request_context()` method from :class:`Permissions`. This was adding unjustified complexity. Instead, inheritance and `super()` calls can be used.
* Added new operator: `Cmp()`. This allows to compare permission rules to request object even if they are not currently available in the method scope. Also, this prevents exceptions from non-existing relations (e.g. `request.user.company` while `company` can be null).
* Simplification. Removed dependency on Django patches or middleware tricks. Now if a user is anonymous and permissions are checked, and they fail on specific attributes of the `User` instance (e.g. `get_profile()`), user will be denied access for that specific rule by default.
* Updated Django Debug Toolbar integration.
* Added support for passing permission rules to classes having permissions already defined. This will cause all rules to be merged using AND (&). For example, following is now possible:


:file:`accounts/permissions.py`

.. code-block:: python

    class ContentEditablePermissions(Permissions):

        def get_permissions(self, request, **kwargs):
            try:
                request.content = Content.objects.get(slug=kwargs.get('slug'))
            except Content.DoesNotExist:
                request.content = None
            return P(user__is_author_of=Arg('content')) | P(content__publisher=Cmp('user.publisher'))


:file:`content/views.py`

.. code-block:: python

    class ContentUpdateView(DjangoViewMixin, UpdateView):

        model = Content
        template_name = 'content/content_edit.html'
        form_class = ContentCreateUpdateForm
        permissions_class = ContentEditablePermissions(
            P(content__can_change_price=True)
        )

So the final result would be:

.. code-block:: python

    request.content.can_change_price() & (request.user.is_author_of(request.content) | (request.content.publisher == request.user.publisher))

1.1.4
=====

* Fixed Django debug toolbar panel.
* Removed caching (`explanation <https://github.com/thinkingpotato/django-permissionsx/issues/21>`_).

1.1.3
=====

* Added in-memory caching (``settings.PERMISSIONSX_CACHING``).
* Added tests for Django Views, settings and overrides.
* Changed the way overrides work. Few things got simplified by the way. Now it is possible to use multiple overrides attached to :class:`P` objects, not the top-level :class:`Permissions`.

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

