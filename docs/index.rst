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

:mod:`django-permissionsx` is an alternative to `Django permissions system <https://docs.djangoproject.com/en/1.5/topics/auth/default/#topic-authorization>`_. The main difference is that this package does not store authorization logic in database, but instead allows defining permissions on the view class level using concise syntax and performs authorization checks against `HttpRequest <https://docs.djangoproject.com/en/1.5/ref/request-response/#httprequest-objects>`_ object.

You will find that defining permissions is similar to filtering QuerySets and `complex lookups with Q objects <https://docs.djangoproject.com/en/1.5/topics/db/queries/#complex-lookups-with-q-objects>`_. For example:

.. code-block:: python

    P(user__is_authenticated=True) & P(P(user__is_staff=True) | P(user__is_superuser=True))

means that the user will be granted access if is logged in **and** is either a staff member, **or** a superuser.

Currently :mod:`django-permissionsx` can be used with Django class-based views, templates and `django-tastypie <https://github.com/toastdriven/django-tastypie/>`_ authorization.

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


