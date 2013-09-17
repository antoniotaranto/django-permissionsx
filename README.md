# django-permissionsx

Authorization for Django: extended, experimental, X...

## How it works

This package works by leveraging the fact that Django request object is easily accessible and usually holds enough information to perform authorization process. No more ```has_perm```, assigning to groups etc. Maybe you like it, I just can't get used to it.

If the request object has no information you need to check permissions, you may use middleware. For example, if ```settings.AUTH_PROFILE_MODULE``` is enabled, ```permissionsx.middleware.PermissionsXProfileMiddleware``` copies user's profile to the request object (so it can be later used for checking permissions, see below) and if the user is anonymous - it attaches an instance of ```AnonymousProfile```.

I was trying to do my best to follow Django conventions. You will find that defining permissions is similar to filtering QuerySets.

Currently ```django-permissionsx``` can be used with Django class-based views and ```django-tastypie``` authorization. What is cool about this approach, is that you define your inheritable and mixable permissions **once** and use them both in views and API calls! And it's easily customizable, so you may expect new extensions coming soon.


## Installation

1. Install ```django-permissionsx``` package:

        pip install django-permissionsx

2. Add a middleware (if using 1-1 profiles):

        MIDDLEWARE_CLASSES = (
            ...
            'permissionsx.middleware.PermissionsXProfileMiddleware',
        )

3. Add permissions to your views, e.g.:

        from permissionsx.contrib.django_permissions import PermissionsViewMixin
        from permissionsx.models import P
        from permissionsx.models import Permissions


        class UserPermissions(Permissions):

            permissions = P(user__is_authenticated=True)


        class PublicListView(PermissionsViewMixin, ListView):

            queryset = Item.objects.all()
            permissions = UserPermissions

4. If you are not going to reuse your permissions you can also use a simplified syntax:

        class RestrictedListView(PermissionsViewMixin, ListView):

            queryset = Item.objects.all()
            permissions = P(user__is_staff) | P(profile__full_name='The Boss')


5. And you're done!

## Examples


### accounts/models.py

        class Profile(models.Model):

            user = models.OneToOneField('auth.User')
            is_author = models.BooleanField()
            is_editor = models.BooleanField()
            is_administrator = models.BooleanField()

### accounts/permissions.py

        from permissionsx.models import Permissions
        from permissionsx.models import P


        class UserPermissions(Permissions):

            permissions = P(user__is_authenticated=True)


        class AuthorPermissions(Permissions):

            permissions = P(profile__is_author=True) | P(profile__is_editor=True) | P(profile__is_administrator=True)


        class StaffPermissions(Permissions):

            permissions = P(profile__is_editor=True) | P(profile__is_administrator=True)


        class VariaPermissions(Permissions):

            def get_permissions(self, request=None):
                # NOTE: Please note that the rules below make no sense.
                return ~P(profile__is_editor=True) & P(P(user__pk=request.user.pk) | P(user__username='Mary'))

### articles/views.py

        from permissionsx.contrib.django_permissions import PermissionsViewMixin

        from newspaper.accounts.permissions import (
            AuthorPermissions,
            StaffPermissions,
        )


        class ArticleListView(PermissionsViewMixin, ListView):

            queryset = Article.objects.filter(is_published=True)
            permissions = AuthorPermissions


        class ArticleDeleteView(PermissionsViewMixin, DeleteView):

            model = Article
            success_url = reverse_lazy('article_list')
            permissions = StaffPermissions

### articles/api.py (Tastypie)

        from permissionsx.contrib.tastypie_permissions import PermissionsAuthorization

        from newspaper.profiles.permissions import UserPermissions
        from newspaper.profiles.permissions import StaffPermissions
        from newspaper.articles.models import Article
        from newspaper.articles.models import Comment


        class StaffOnlyAuthorization(PermissionsAuthorization):

            permissions = StaffPermissions


        class CommentingAuthorization(PermissionsAuthorization):

            permissions = UserPermissions

            def create_list(self, object_list, bundle):
                raise Unauthorized()

            def update_list(self, object_list, bundle):
                raise Unauthorized()

            def update_detail(self, object_list, bundle):
                # NOTE: This overrides `self.permissions` just for this single case.
                return self.check_permissions(bundle.request, StaffPermissions)

            def delete_list(self, object_list, bundle):
                raise Unauthorized()

            def delete_detail(self, object_list, bundle):
                raise Unauthorized()

## CHANGELOG

### 0.0.8

* This version is backward **incompatible**.
* Changed syntax to follow QuerySet filtering convention.
* Sadly, tests are gone. Need to write new ones, what will not happen until 1.0.0 release.
* Example project's gone. Will be back at a different URL.
* ```PERMISSIONSX_DEFAULT_URL``` was renamed to ```PERMISSIONSX_REDIRECT_URL```.
* New setting was added: ```PERMISSIONSX_LOGOUT_IF_DENIED```.

## Coming soon (?)

* Caching permission check results.
* Bring the same philosophy to the ORM level.

## Contact

If there is anything I can help with, or there is something worth adding, or there are just any comments on this stuff or bugs you would like to report, please get in touch via Github, Twitter ([@thinkingpotato](http://twitter.com/thinkingpotato/)) or @freenode/#django.
