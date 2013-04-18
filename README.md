# django-permissionsx

Authorization for Django Class-Based Views.

## How it works

This package works by adding to requests objects that are required for checking permissions. Objects are added by invoking static method ```get_request_context()``` of a view, while the logic is held in ```permissions``` attribute. ```PermissionsXMiddleware``` either raises ```django.core.exceptions.PermissionDenied``` or redirects to another view (by using URL name defined in ```urls.py```).

### Working example

**Have a look at the example you will find in source package.** You can run it simply by installing ```django-permissionsx``` somewhere in your Python path and by running:

        (example_virtualenv)demo:~/projects/django-permissionsx/example$ ./manage.py runserver

Now point your browser to http://127.0.0.1:8000

## Installation

1. Install ```django-permissionsx``` package:

        pip install django-permissionsx

2. Add a new middleware:

        MIDDLEWARE_CLASSES = (
            ...
            'permissionsx.middleware.PermissionsXMiddleware',
            ...

3. Add permissions to your views (which means: if user is not logged in, **redirect (->)** them to default login view):

        permissions = ['user__is_authenticated->auth_login']

4. You're done!

## Syntax

Permissions are defined by setting ```permissions``` attribute on a view class.

### Basic permission

#### Ex.:
        permissions = ['user__is_authenticated']

### Redirects

If permission check ```is_authenticated``` fails, user will be redirected to URL named ```auth_login```.

#### Ex.:
        permissions = ['user__is_authenticated->auth_login']
        
### Multiple permissions

These permissions will be checked according to the order of the list. If the first one fails, and there is no redirect defined, ```permissionsx``` will raise ```PermissionDenied``` exception.

#### Ex.:
        permissions = ['user__is_authenticated', 'profile__is_boss']

### Multiple permissions where only one needs to be ```True``` (boolean OR)

In this case user will be able to access the view if:
* is logged in (default Django authorization mechanism);
* ```self.request.test.assigned_to(self.request.profile) == True```;
* ```self.request.profile.is_engineer == True```.

If the user is not logged in, they will be instantly redirected to login page.

#### Ex.:
        permissions = ['user__is_authenticated->login', ('test__assigned_to:profile', 'profile__is_engineer')]
        
### Relations with other request objects

This is essentially a shortcut for saying:
* ```self.request.profile.owns(self.request.document)```

Where:

        class Profile(models.Model):
                [...]
                def owns(self, obj):
                            return obj.owner == self

#### Ex.:
        permissions = ['profile__owns:document']

## Examples

Here is a list of some use cases you may be interested in:

        permissions = ['user__is_authenticated']
        permissions = ['user__is_authenticated->auth_login']
        permissions = ['user__is_authenticated', 'profile__is_boss']
        permissions = ['user__is_authenticated', 'profile__is_boss_or_leader']
        permissions = ['user__is_authenticated->auth_login', ('test_scenario__assigned_to:profile', 'profile__is_engineer', 'profile__is_manager')]
        permissions = ['profile__owns:document']
        permissions = ['profile__is_boss_or_leader', 'document__editable_by:profile']
        permissions = ['profile__has_purchased:document']
        permissions = ['document__is_published']

### profile__*

In order to use the convention above, you need ```PermissionsXProfileMiddleware```:

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'permissionsx.addons.middleware.PermissionsXProfileMiddleware',
        'permissionsx.middleware.PermissionsXMiddleware',
        ...
    )

What it does is simply assigning ```User.get_profile()``` instance to every request, so permissions mechanism can do checks on that. ```__is_boss``` and ```__has_purchased``` are Profile class methods that simply return ```True``` or ```False```, depending on parameter (in case of ```has_purchased()```).

You must also alternate your ```settings.py``` to point to "dummy" Profile class that will answer permissions checks with defaults for anonymous users, e.g.:

    PERMISSIONS_ANONYMOUS_ACTOR = 'myapplication.profiles.models.AnonymousActor'

And in your ```models.py```:

    class AnonymousActor(object):

        def has_purchased(self, document):
            return False

### *__owns:

In case of:

    permissions = ['profile__owns:document']

There are two objects you need to have on your requests for this view: ```profile``` and ```document```. ```Profile``` can ba managed using middleware above, while ```document``` needs to be added for this view specifcally. This is usually requirement for other views, so what I use is a simple mixin class:

    class DocumentRequestContext(object):

        @staticmethod
        def get_request_context(**kwargs):
            return {
                'document': get_object_or_404(Document, slug=kwargs.get('document_slug')),
            }

So the final view class would look like this:

    class DocumentUpdateView(UpdateView, DocumentRequestContext):

        template_name = 'documents/document_edit.html'
        form_class = DocumentCreateUpdateForm
        permissions = ['profile__is_boss_or_leader', 'document__editable_by:profile']
            
        def get_object(self):
            return self.request.document

The ```Profile``` class extended by a method:

    class Profile(models.Model):
        ...
        def is_boss_or_leader(self):
            return self.is_boss or self.is_leader

And the ```Document``` one by:

    class Document(models.Model):
        ...
        def editable_by(self, profile):
            return self.author == profile or self.company == profile.company

Finally, ```AnonymousActor``` may look like:

    class AnonymousActor(object):
        is_boss = False
        is_leader = False
        company = None

        def editable_by(self, profile):
            return False

        def is_boss_or_leader(self):
            return False

## Contact / More info

If there is anything I can help with, or there is something worth adding, or there are just any comments on this stuff or bugs you would like to report, please get in touch via Github, Twitter ([@thinkingpotato](http://twitter.com/thinkingpotato/)) or @freenode/#django.
