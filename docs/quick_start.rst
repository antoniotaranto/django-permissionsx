===========
Quick Start
===========


1. Install :mod:`django-permissionsx` package:
----------------------------------------------

.. code-block:: bash

        pip install django-permissionsx

2. Define permissions in a module of your choice:
-------------------------------------------------

.. code-block:: python

        from permissionsx.models import P
        from permissionsx.models import Permissions


        class ManagerPermissions(Permissions):

            permissions = P(user__is_staff=True) & P(user__is_manager=True)


3. Add permissions to your views, e.g.:
---------------------------------------

.. code-block:: python

        from django.views.generic import ListView

        from permissionsx.contrib.django import DjangoViewMixin

        from newspaper.profiles.permissions import ManagerPermissions


        class AuthenticatedListView(DjangoViewMixin, ListView):

            queryset = Item.objects.all()
            permissions_class = Permissions(
                P(user__is_authenticated=True)
            )


        class ManagerListView(DjangoViewMixin, ListView):

            queryset = Item.objects.all()
            permissions_class = ManagerPermissions


4. Don't forget to add :mod:`permissionsx` to your :attr:`INSTALLED_APPS`:
--------------------------------------------------------------------------

.. code-block:: python

        INSTALLED_APPS = (
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.staticfiles',
            [...]
            'permissionsx',

5. Apply permissions in templates if you need:
----------------------------------------------

.. code-block:: python

        {% load permissionsx_tags %}
        {% permissions 'newspaper.profiles.permissions.ManagerPermissions' as user_is_manager %}

        <ul id="utility-navigation">
            {% if user_is_manager %}
                <a href="#">Publish article</a>
            {% endif %}
        </ul>


6. That's all!
--------------

User will be redirected to :attr:`LOGIN_URL` by default, if:

* not logged in and tries to access :class:`AuthenticatedListView`;
* not a staff member, :attr:`request.user.profile.is_manager` is set to :obj:`False` and tries to access :class:`ManagerListView`;
* *Publish article* option will be displayed only if user meets :class:`ManagerPermissions` conditions.
