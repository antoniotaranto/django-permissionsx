# django-permissionsx

Authorization for Django Class-Based Views.

## How it works

This package works by extending requests with objects that are required for checking permissions. These may be objects referenced by specific URL (e.g. slug or PK lookups) or objects performing checks on other objects (e.g. ```User``` instance which is available by default in each request).

Objects may be added either by invoking static method ```get_request_context()``` on a view level, or by using custom middleware (see ```permissionsx.tests.middleware``` for example). Middleware scenario is most useful when you expect using given class/instance in most of the views.

The logic is held in ```permissions``` attribute of a ```View``` class. ```PermissionsXMiddleware``` either raises ```django.core.exceptions.PermissionDenied``` or redirects to another view (by using URL name defined in ```urls.py```) if conditions are not met.

### Working example

**Have a look at the example you will find in the source package.** You can run it simply by installing ```django-permissionsx``` somewhere in your Python path and by running:

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

## Examples

Here is a list of some use cases you may be interested in:

        permissions = ['user__is_authenticated']
        permissions = ['user__is_authenticated->auth_login']
        permissions = ['user__is_authenticated', 'profile__is_boss']
        permissions = ['user__is_authenticated->auth_login', ('test_scenario__assigned_to:profile', 'profile__is_engineer', 'profile__is_manager')]
        permissions = ['profile__owns:document']
        permissions = ['profile__has_purchased:document']
        permissions = ['document__is_published']

## Syntax

Permissions are defined by setting ```permissions``` attribute on a view class.

### Basic permission

#### Ex.:
        permissions = ['user__is_authenticated']

### Redirects

#### Ex.:
        permissions = ['user__is_authenticated->auth_login']

If permission check ```is_authenticated``` fails, user will be redirected to URL named ```auth_login```.
        
### Multiple permissions

#### Ex.:
        permissions = ['user__is_authenticated', 'profile__is_boss']

These permissions will be checked according to the order of the list. If the first one fails, and there is no redirect defined, ```permissionsx``` will raise ```PermissionDenied``` exception.

### Multiple permissions where only one needs to be ```True``` (boolean OR)

#### Ex.:
        permissions = ['user__is_authenticated->login', ('test__assigned_to:profile', 'profile__is_engineer')]

In this case user will be able to access the view if:

* is logged in (default Django authorization mechanism);
* ```self.request.test.assigned_to(self.request.profile) == True```;
* ```self.request.profile.is_engineer == True```.

If the user is not logged in, they will be instantly redirected to login page.

### Relations with other request objects

#### Ex.:
        permissions = ['profile__owns:document']

This is essentially a shortcut for saying:

* ```self.request.profile.owns(self.request.document)```

Where:

        class Profile(models.Model):
                [...]
                def owns(self, obj):
                            return obj.owner == self

### Explanation of double underscore (*__owns):

In case of:

    permissions = ['profile__owns:document']

There are two objects you need to have on your requests for this view: ```profile``` and ```document```. ```Profile``` can ba managed using middleware above, while ```document``` needs to be added for this view specifcally. This is usually requirement for other views, so you can use is a simple mixin class:

    class DocumentRequestContext(object):

        @staticmethod
        def get_request_context(request, **kwargs):
            return {
                'document': get_object_or_404(Document, slug=kwargs.get('document_slug')),
            }

And then:

        class DocumentUpdateView(UpdateView, DocumentRequestContext):
                [...]

## Custom middleware

In Django 1.4.x there are no customizable User models, so if you need more sophisticated authorization logic than ```is_staff``` or ```is_authenticated```, you would use middleware to attach ```Profile``` instance to each request, e.g.:

*middleware.py*:

        from yourproject.app.models import AnonymousUserProfile


        class PermissionsXProfileMiddleware(object):

            def process_request(self, request):
                assert hasattr(request, 'user'), 'PermissionsXProfileMiddleware requires AuthenticationMiddleware to be installed.'
                try:        
                    request.profile = request.user.get_profile()
                except (AttributeError, ObjectDoesNotExist):
                    request.profile = AnonymousUserProfile()

Note that there is ```AnonymousUserProfile``` assigned instead of ```UserProfile``` instance if exception is raised. This is because you must ensure the ```request.profile``` is available for each view no matter a user is anonymous or not, for the sake of consistency.

*settings.py*:

        MIDDLEWARE_CLASSES = (
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'yourproject.app.middleware.PermissionsXProfileMiddleware',
            'permissionsx.middleware.PermissionsXMiddleware',
            [...]
        )

*models.py*:

        class Document(models.Model):

            user = models.ForeignKey('auth.User')


        class UserProfile(models.Model):

            def has_purchased(self, document):
                return document.user == self.user


        class AnonymousUserProfile(object):

            def has_purchased(self, document):
                return False

*view.py*:

        class DocumentUpdateView(UpdateView):

            template_name = 'documents/document_edit.html'
            form_class = DocumentCreateUpdateForm
            permissions = ['profile__has_purchased:document']

            @staticmethod
            def get_request_context(request, **kwargs):
                return {
                    'document': get_object_or_404(Document, slug=kwargs.get('document_slug')),
                }

            def get_object(self):
                return self.request.document

## Coming soon

* Caching permission check results.
* Bring the same philosophy to the ORM level.

## Contact

If there is anything I can help with, or there is something worth adding, or there are just any comments on this stuff or bugs you would like to report, please get in touch via Github, Twitter ([@thinkingpotato](http://twitter.com/thinkingpotato/)) or @freenode/#django.
