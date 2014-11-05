[![Build Status](https://travis-ci.org/thinkingpotato/django-permissionsx.png?branch=master)](https://travis-ci.org/thinkingpotato/django-permissionsx)
[![Coverage Status](https://coveralls.io/repos/thinkingpotato/django-permissionsx/badge.png)](https://coveralls.io/r/thinkingpotato/django-permissionsx)
[![Latest Version](https://pypip.in/v/django-permissionsx/badge.png)](https://pypi.python.org/pypi/django-permissionsx/)
[![Downloads](https://pypip.in/d/django-permissionsx/badge.png?period=month)](https://pypi.python.org/pypi/django-permissionsx/)
[![License](https://pypip.in/license/django-permissionsx/badge.png)](https://pypi.python.org/pypi/django-permissionsx/)

# django-permissionsx

* [Documentation](http://django-permissionsx.readthedocs.org/)
* [Changelog](http://django-permissionsx.readthedocs.org/en/latest/changelog.html)
* [Python package](http://pypi.python.org/pypi/django-permissionsx/)
* [Example project](http://github.com/thinkingpotato/django-permissionsx-example)

## Feedback needed!

If you find this package useful, please let me know about your experiences. If there are any bugs or things that in your opinion could be improved, please report using Github issues. I really want to make it bulletproof, so any input you provide is greatly appreciated!

_Robert_

## Quick Start

### 1. Install *django-permissionsx* package:

        pip install django-permissionsx

### 2. Define permissions in a module of your choice:

        from permissionsx.models import P
        from permissionsx.models import Permissions


        class ManagerPermissions(Permissions):

            rules = P(user__is_staff=True) & P(user__has_company_assigned=True)


### 3. Add permissions to your views, e.g.:

        from permissionsx.contrib.django.views import PermissionsListView

        from example.profiles.permissions import ManagerPermissions


        class AuthenticatedListView(PermissionsListView):

            queryset = Item.objects.all()
            permissions = Permissions(
                P(user__is_authenticated=True)
            )


        class ManagerListView(PermissionsListView):

            queryset = Item.objects.all()
            permissions = ManagerPermissions()


### 4. Don't forget to add *permissionsx* to your *INSTALLED_APPS*:

        INSTALLED_APPS = (
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.staticfiles',
            [...]
            'permissionsx',

### 5. Now add request context processor, so you can use permissions in your templates:

        TEMPLATE_CONTEXT_PROCESSORS = (
            [...]
            'django.core.context_processors.request',
            [...]
        )

### 6. Apply permissions in templates if you need:

        {% load permissionsx_tags %}
        {% block content %}
        {% permissions 'example.profiles.permissions.ManagerPermissions' as user_is_manager %}
        <ul id="utility-navigation">
            {% if user_is_manager %}
                <a href="#">Publish article</a>
            {% endif %}
        </ul>
        {% endblock content %}

### 7. That's all!

User will be redirected to *LOGIN_URL* by default, if:

* not logged in and tries to access *AuthenticatedListView*;
* not a staff member, *request.user.profile.is_manager* is set to *False* and tries to access *ManagerListView*;
* *Publish article* option will be displayed only if user meets *ManagerPermissions* conditions.
