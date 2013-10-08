[![Build Status](https://travis-ci.org/thinkingpotato/django-permissionsx.png?branch=master)](https://travis-ci.org/thinkingpotato/django-permissionsx)

# django-permissionsx

Authorization for Django: extended, experimental, X...

## How it works

This package works by leveraging the fact that Django request object is easily accessible and usually holds enough information to perform authorization process. No more ```has_perm```, assigning to groups etc. Maybe you like it, I just can't get used to it.

If the request object has no information you need to check permissions, you can add it at the `Permissions` class level using `set_request_objects()` method.

I was trying to do my best to follow Django conventions. You will find that defining permissions is similar to filtering QuerySets.

Currently ```django-permissionsx``` can be used with Django class-based views, templates and ```django-tastypie``` authorization. What is cool about this approach, is that you define your inheritable and mixable permissions **once** and use them in views, templates and API calls! And it's easily customizable, so you may expect new extensions coming soon.


## Installation & Usage

1. Install ```django-permissionsx``` package:

        pip install django-permissionsx

2. Define permissions in a module of your choice (like permissions.py):

        from permissionsx.models import P
        from permissionsx.models import Permissions


        class UserPermissions(Permissions):

            permissions = P(user__is_authenticated=True)

3. Add permissions to your views, e.g.:

        from your_project.permissions import UserPermissions
        from permissionsx.contrib.django import DjangoViewMixin


        class PublicListView(DjangoViewMixin, ListView):

            queryset = Item.objects.all()
            permissions_class = UserPermissions

4. Don't forget to add `permissionsx` to your `INSTALLED_APPS`:

        INSTALLED_APPS = (
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.staticfiles',
            [...]
            'permissionsx',

5. Also, you may find `django-debug-toolbar` helpful in assigning right permissions, just add:

        DEBUG_TOOLBAR_PANELS = (
            [...]
            'permissionsx.contrib.django_debug_toolbar.PermissionsDebugPanel',
        )

6. You're done!

## Settings

**PERMISSIONSX_REDIRECT_URL**

Defaults to `settings.LOGIN_URL`.

If user has not been granted permission to access a Django view, redirect to `PERMISSIONSX_REDIRECT_URL`.

**PERMISSIONSX_LOGOUT_IF_DENIED**

Defaults to `False`.

If user has not been granted permission to access a Django view, log the user out before redirecting to `PERMISSIONSX_REDIRECT_URL`.

**PERMISSIONSX_DEBUG**

Defaults to `False`.

If turned on, logger named `permissionsx` will be available for debugging purposes.

## Things good to know

* If a user is being redirected while not being logged in (`request.user.is_authenticated()`), current `request.get_full_path()` will be added to the URL as `next` parameter.


## More examples

### Complex example

#### profiles/models.py

        class Profile(models.Model):

            user = models.OneToOneField('auth.User')
            is_author = models.BooleanField()
            is_editor = models.BooleanField()
            is_administrator = models.BooleanField()

        class AnonymousProfile(object):

            user = None
            is_author = False
            is_editor = False
            is_administrator = False

#### profiles/permissions.py

        from permissionsx.models import P
        from permissionsx.models import Permissions

        from newspaper.profiles.models import AnonymousProfile
        from newspaper.articles.models import Article


        class ProfilePermissions(Permissions):

            def set_request_objects(self, request, **kwargs):
                if request.user.is_anonymous():
                    request.user.get_profile = lambda: AnonymousProfile()


        class UserPermissions(Permissions):

            permissions = P(user__is_authenticated=True)


        class AuthorPermissions(ProfilePermissions):

            permissions = P(user__get_profile__is_author=True) | P(user__get_profile__is_editor=True) | P(user__get_profile__is_administrator=True)


        class StaffPermissions(ProfilePermissions):

            permissions = P(user__get_profile__is_editor=True) | P(user__get_profile__is_administrator=True)

        class VariaPermissions(ProfilePermissions):

            def get_permissions(self, request=None):
                # NOTE: Please note that the rules below make no sense.
                return ~P(user__get_profile__is_editor=True) & P(P(user__pk=request.user.pk) | P(user__username='Mary'))

#### articles/views.py

        from permissionsx.contrib.django import DjangoViewMixin

        from newspaper.profiles.permissions import (
            AuthorPermissions,
            StaffPermissions,
        )


        class ArticleListView(DjangoViewMixin, ListView):

            queryset = Article.objects.filter(is_published=True)
            permissions_class = AuthorPermissions


        class ArticleDeleteView(DjangoViewMixin, DeleteView):

            model = Article
            success_url = reverse_lazy('article_list')
            permissions_class = StaffPermissions

#### articles/templates/articles/comment_list.html

        {% load permissionsx_tags %}

        {% permissions "newspaper.profiles.permissions.StaffPermissions" as comment_blocking_granted %}

        {% if comment_blocking_granted %}
            <a href="#" class="btn block-comment" data-comment-id="{{ comment.pk }}">Block this comment</a>
        {% endif %}

        {% comment %}NOTE: Checks permissions for objects in a list.{% endcomment %}
        {% for object in object_list %}
            {% permissions "newspaper.profiles.permissions.AuthorIfNotPublishedPermissions" slug=object.slug as can_change_object_granted %}
            {% if can_change_object_granted %}
                <a href="{% url 'article_update' object.slug %}" class="bt btnn-success">Edit</a>
                <a href="{% url 'article_delete' object.slug %}" class="btn btn-danger">Delete</a>
            {% endif %}
                <a href="{% url 'article_view' object.slug %}" class="btn btn-whatever">View</a>
        {% endfor $}

### Using permission classes with Tastypie

#### articles/api.py

        from permissionsx.contrib.tastypie import TastypieAuthorization

        from newspaper.profiles.permissions import UserPermissions
        from newspaper.profiles.permissions import StaffPermissions
        from newspaper.articles.models import Article
        from newspaper.articles.models import Comment


        class StaffOnlyAuthorization(TastypieAuthorization):

            permissions_class = StaffPermissions


        class CommentingAuthorization(TastypieAuthorization):

            permissions_class = UserPermissions

            def create_list(self, object_list, bundle):
                raise Unauthorized()

            def update_list(self, object_list, bundle):
                raise Unauthorized()

            def update_detail(self, object_list, bundle):
                # NOTE: This overrides `self.permissions` just for this single case.
                return StaffPermissions().check_permissions(bundle.request)

            def delete_list(self, object_list, bundle):
                raise Unauthorized()

            def delete_detail(self, object_list, bundle):
                raise Unauthorized()

### Response with custom message and redirect URL

#### articles/views.py

        from django.contrib import messages

        from permissionsx.contrib.django import MessageRedirectView


        class NotStaffRedirectView(MessageRedirectView):

            message = (messages.warning, _('Insufficient permissions!'))
            redirect_url = reverse_lazy('help_screen')


        class ArticleCreateView(DjangoViewMixin, CreateView):

            model = Article
            success_url = reverse_lazy('article_list')
            form_class = ArticleCreateForm
            permissions_class = StaffPermissions
            permissions_response_class = NotStaffRedirectView


### Reusing permissions and passing request variables

#### articles/permissions.py

        editor_or_administrator = P(user__get_profile__is_editor=True) | P(user__get_profile__is_administrator=True)

        class AuthorIfNotPublishedPermissions(ProfilePermissions):

            permissions = editor_or_administrator

            def get_permissions(self, request=None):
                return self.permissions | P(P(user__get_profile__is_author=True) & P(article__is_published=False) & P(article__author=request.user))

            def set_request_objects(self, request, **kwargs):
                super(AuthorIfNotPublishedPermissions, self).set_request_objects(request, **kwargs)
                request.article = Article.objects.get(slug=kwargs.get('slug'))


### Best practices: get permissions in the top level template

#### templates/base.html

        {% load permissionsx_tags %}
        {% permissions 'newspaper.profiles.permissions.AuthorPermissions' as user_is_author %}
        {% permissions 'newspaper.profiles.permissions.StaffPermissions' as user_is_staff %}
        {% permissions 'newspaper.profiles.permissions.AdministratorPermissions' as user_is_administrator %}

        <ul id="utility-navigation>
            {% if user_is_administrator %}
                <a href="#">Add a new author</a>
            {% endif %}
            {% if user_is_staff %}
                <a href="#">Publish article</a>
            {% endif %}
        </ul>

#### templates/articles/article_detail.html

        {% extends "base.html" %}

        {% if user_is_author %}
            <a href="#">Write article</a>
        {% endif %}

## Compatibility

### Python 2.7.x

|                 |  django-permissionsx 1.0.0  |
| :-------------: | :-------------------------: |
| Django 1.4.8    |           &#10004;          |
| Django 1.5.4    |           &#10004;          |
| Tastypie 0.9.16 |           &#10004;          |
| Tastypie 0.10.0 |           &#10004;          |

### Python 3.3.x

**NOTE**: `django-debug-toolbar` is not currently available for Python 3.3.x.

|                 |  django-permissionsx 1.0.0  |
| :-------------: | :-------------------------: |
| Django 1.5.4    |           &#10004;          |
| Tastypie 0.10.0 |           &#10004;          |

## CHANGELOG

### 1.1.0

* New syntax possible for retrieving related objects, e.g. `P(user__get_profile__related_object__is_something=True)`.

### 1.0.0

* Added support for custom response classes (e.g. for changing redirect URL, adding custom user message).
* Added tests for checking permissions.
* Minor fixes and improvements.

### 0.0.9

* Renamed class-level `permissions` to `permissions_class`.
* Dropped support for simple permissions defining for the benefit of greater flexibility.
* Renaming and refactoring, again. Good stuff: managed to get rid of middleware and a class. Things got largely simplified in general.
* Added support for Django templates, including per-object checks.
* Requirement: django-classy-tags.

### 0.0.8

* This version is backward **incompatible**.
* Changed syntax to follow QuerySet filtering convention.
* Sadly, tests are gone. Need to write new ones, what will not happen until 1.0.0 release.
* Example project's gone. Will be back at a different URL.
* ```PERMISSIONSX_DEFAULT_URL``` was renamed to ```PERMISSIONSX_REDIRECT_URL```.
* New setting was added: ```PERMISSIONSX_LOGOUT_IF_DENIED```.
