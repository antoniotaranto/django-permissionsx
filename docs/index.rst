===============================================
Welcome to django-permissionsx's documentation!
===============================================

* Version:
    - |version|
* Python Package:
    - `<http://pypi.python.org/pypi/django-permissionsx/>`_
* Source code:
    - `<http://github.com/thinkingpotato/django-permissionsx/>`_
* Bug tracker:
    - `<http://github.com/thinkingpotato/django-permissionsx/issues/>`_

Introduction
============

**django-permissionsx** is an alternative to `Django permissions system <https://docs.djangoproject.com/en/1.5/topics/auth/default/#topic-authorization>`_. The main difference is that this package does not store authorization logic in database, but instead allows defining permissions on the view level using concise syntax (similar to complex lookups using `Q`) and performs authorization checks against `HttpRequest <https://docs.djangoproject.com/en/1.5/ref/request-response/#httprequest-objects>`_ object. You could think of it as a wrapper around common patterns such as `@login_required` decorator or checking `request.user.is_authenticated()`.

You will find that defining permissions is similar to filtering QuerySets and `complex lookups with Q objects <https://docs.djangoproject.com/en/1.5/topics/db/queries/#complex-lookups-with-q-objects>`_. For example:

.. code-block:: python

    P(user__is_authenticated=True) & P(P(user__is_staff=True) | P(user__is_superuser=True))

means that the user will be granted access if is logged in **and** is either a staff member, **or** a superuser.

The goal of this project is to make authorization related code as much reusable and consistent as possible. Therefore, permissions can be easily used for multiple views, inherited, used in templates or for building mobile API using `django-tastypie <https://github.com/toastdriven/django-tastypie/>`_.

Contents
========

.. toctree::
    :maxdepth: 1

    quick_start
    settings
    tutorial/index
    notes
    compatibility

.. toctree::
    :maxdepth: 2

    changelog
    reference/index

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


