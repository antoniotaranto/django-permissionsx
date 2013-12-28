========
Tutorial
========

.. contents:: Table of Contents

Overview
========

P
-
:class:`permissionsx.models.P`

:class:`P` is the smallest building block. Permissions are defined using keyword arguments, for example:

.. code-block:: python

    P(user__get_profile__is_public=True)

It means that the value of ``request.user.get_profile().is_public`` will be compared with ``True``. If the final result is ``True``, the user will be granted access. Otherwise the user will be redirected to the ``settings.LOGIN_URL`` by default.

:class:`P` objects can be negated and combined using ~, & and | operators, exactly the same way as `Q objects <https://docs.djangoproject.com/en/1.5/topics/db/queries/#complex-lookups-with-q-objects>`_.

Optionally, for more advanced workflows, :class:`P` can be passed additional two keyword arguments for overriding default behavior:

* :attr:`if_false`
* :attr:`if_true`

It is useful in situations where user needs to be redirected to different URLs when specific conditions are met. For example, if user:

* is not authenticated, redirect to login view by default;
* is authenticated, but has insufficient permissions (e.g. needs to upgrade account), redirect to a view with payment options and show message using :mod:`django.contrib.messages`;
* is authenticated and has sufficient permissions, let in.

Have a look at `Response with action overridden on a P() level`_ on how overrides can be used.

Arg
---
:class:`permissionsx.models.Arg`

:class:`Arg` is used when permissions checking involves passing parameter to a method of an object attached to the request. This is most often used for checking access to specific objects, e.g.:

.. code-block:: python

    P(user__get_profile__has_access_to=Arg('invoice'))

Note that :class:`Arg` parameter is passed as a string. Basically, it is equivalent to:

.. code-block:: python

    request.user.get_profile().has_access_to(request.invoice)


Cmp
---
:class:`permissionsx.models.Cmp`

:class:`Cmp` is used when permissions require comparing values of objects attached to the request even if the compared attributes are not currently available in the method scope. Also, :class:`Cmp` prevents exceptions from non-existing relations (e.g. `request.user.company` while `company` can be null).

.. code-block:: python

    P(company__main_address__city=Cmp('user.address.city'))

Note that :class:`Cmp` parameter is passed as a string. It is equivalent to:

.. code-block:: python

    request.company.main_address.city == request.user.address.city

So in this scenario, view is passed e.g. `kwargs` containing `{'slug': 'company-xyz'}`. Company XYZ instance is retrieved from database and its headquarter's city is compared to the one of a user currently accessing view. If these match, user is allowed to view page, can be redirected, shown a message etc.


Permissions
-----------
:class:`permissionsx.models.Permissions`

:class:`Permissions` may be passed as an instance or a class to Django views or Tastypie authorization classes and it encapsulates :class:`P` definitions, e.g.:

.. code-block:: python

        class UserPermissions(Permissions):

            permissions = P(user__is_authenticated=True)


        class ArticleDetailView(DjangoViewMixin, DetailView):

            model = Article
            permissions_class = UserPermissions


        class StaffOnlyAuthorization(TastypieAuthorization):

            permissions_class = UserPermissions


Or the same just without subclassing :class:`Permissions`:

.. code-block:: python

        class ArticleDetailView(DjangoViewMixin, DetailView):

            model = Article
            permissions_class = Permissions(P(user__is_authenticated=True))


And yet another example, this time by reusing single definition:


.. code-block:: python

        is_authenticated = P(user__is_authenticated=True)


        class ArticleDetailView(DjangoViewMixin, DetailView):

            model = Article
            permissions_class = Permissions(is_authenticated)


Attributes:

* :attr:`permissions` - required.


Django
------

DjangoViewMixin
~~~~~~~~~~~~~~~
:class:`permissionsx.contrib.django.DjangoViewMixin`

:class:`DjangoViewMixin` is required by every Django view that uses permissions. E.g.:

.. code-block:: python

    class ArticleDetailView(DjangoViewMixin, DetailView):

        model = Article
        permissions_class = UserPermissions

Attributes:

* :attr:`permissions_class` - required.
* :attr:`permissions_response_class` - optional, defaults to :class:`permissionsx.contrib.django.RedirectView`.

permissions (template tag)
~~~~~~~~~~~~~~~~~~~~~~~~~~
:class:`permissionsx.contrib.django.permissions`

Enables permissions in Django templates. See `Using permissions in templates`_ for an example.

Tastypie
--------

TastypieAuthorization
~~~~~~~~~~~~~~~~~~~~~
:class:`permissionsx.contrib.tastypie.TastypieAuthorization`

Allows using permissions with Tastypie authorization API. See `Integration with Tastypie`_ for an example.

Examples
========

Full Example
------------

:file:`profiles/models.py`

.. code-block:: python

    from django.db import models


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


:file:`profiles/permissions.py`

.. code-block:: python

    from permissionsx.models import P
    from permissionsx.models import Permissions

    from newspaper.profiles.models import AnonymousProfile
    from newspaper.articles.models import Article


    editor_or_administrator = P(user__get_profile__is_editor=True) | P(user__get_profile__is_administrator=True)


    class UserPermissions(Permissions):

        permissions = P(user__is_authenticated=True)


    class AuthorPermissions(Permissions):

        permissions = P(user__get_profile__is_author=True) | editor_or_administrator


    class StaffPermissions(Permissions):

        permissions = editor_or_administrator


:file:`articles/views.py`

.. code-block:: python

    from django.views.generic import (
        ListView,
        DeleteView,
    )
    from django.core.urlresolvers import reverse_lazy

    from permissionsx.contrib.django import DjangoViewMixin

    from newspaper.profiles.permissions import (
        AuthorPermissions,
        StaffPermissions,
    )
    from newspaper.articles.models import Article


    class ArticleListView(DjangoViewMixin, ListView):

        queryset = Article.objects.filter(is_published=True)
        permissions_class = AuthorPermissions


    class ArticleDeleteView(DjangoViewMixin, DeleteView):

        model = Article
        success_url = reverse_lazy('article_list')
        permissions_class = StaffPermissions


:file:`articles/templates/articles/comment_list.html`

.. code-block:: html

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
    {% endfor %}


Integration with Tastypie
-------------------------

:file:`articles/api.py`

.. code-block:: python

    from permissionsx.contrib.tastypie import TastypieAuthorization

    from newspaper.profiles.permissions import (
        UserPermissions,
        StaffPermissions,
    )
    from newspaper.articles.models import (
        Article,
        Comment,
    )


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


Response with custom message and redirect URL
---------------------------------------------

:file:`articles/views.py`

.. code-block:: python

    from django.contrib import messages
    from django.core.urlresolvers import reverse_lazy
    from django.utils.translation import ugettext_lazy as _
    from django.views.generic import CreateView

    from permissionsx.contrib.django import DjangoViewMixin
    from permissionsx.contrib.django import MessageRedirectView

    from newspaper.profiles.permissions import StaffPermissions
    from newspaper.articles.models import Article
    from newspaper.articles.forms import ArticleCreateForm


    class NotStaffRedirectView(MessageRedirectView):

        message = (messages.warning, _('Insufficient permissions!'))
        redirect_url = reverse_lazy('account_login')


    class ArticleCreateView(DjangoViewMixin, CreateView):

        model = Article
        success_url = reverse_lazy('article_list')
        form_class = ArticleCreateForm
        permissions_class = StaffPermissions
        permissions_response_class = NotStaffRedirectView


Response with action overridden on a P() level
----------------------------------------------

:file:`articles/views.py`

.. code-block:: python

    from django.contrib import messages
    from django.core.urlresolvers import reverse_lazy
    from django.utils.translation import ugettext_lazy as _
    from django.views.generic import ListView

    from permissionsx.models import P
    from permissionsx.models import Permissions
    from permissionsx.contrib.django import DjangoViewMixin
    from permissionsx.contrib.django import MessageRedirectView


    class NotStaffRedirectView(MessageRedirectView):

        message = (messages.warning, _('Insufficient permissions!'))
        redirect_url = reverse_lazy('account_login')


    class ArticleListView(DjangoViewMixin, ListView):

        permissions_class = Permissions(
            P(user__is_staff=True, if_false=NotStaffRedirectView.as_view())
        )


Response with action overridden on a P() level (passing view directly)
----------------------------------------------------------------------

:file:`articles/views.py`

.. code-block:: python

    from django.contrib import messages
    from django.core.urlresolvers import reverse_lazy
    from django.utils.translation import ugettext_lazy as _
    from django.views.generic import ListView

    from permissionsx.models import P
    from permissionsx.models import Permissions
    from permissionsx.contrib.django import DjangoViewMixin
    from permissionsx.contrib.django import MessageRedirectView


    class ArticleListView(DjangoViewMixin, ListView):

        permissions_class = Permissions(
            P(user__is_staff=True,
                if_false=MessageRedirectView.as_view(
                    redirect_url=reverse_lazy('account_login'),
                    message=(messages.warning, _('Error!')),
                )
            )
        )


Reusing permissions
-------------------

:file:`articles/permissions.py`

.. code-block:: python

    editor_or_administrator = P(user__get_profile__is_editor=True) | P(user__get_profile__is_administrator=True)

    class AuthorIfNotPublishedPermissions(ProfilePermissions):

        permissions = editor_or_administrator

        def get_permissions(self, request=None, **kwargs):
            return self.permissions | P(
                P(user__get_profile__is_author=True) &
                P(article__is_published=False) &
                P(article__author=request.user)
            )


Setting request objects
-----------------------

:file:`articles/permissions.py`

.. code-block:: python

    class ArticlePermissions(ProfilePermissions):

        def get_permissions(self, request, **kwargs):
            request.article = Article.objects.get(slug=kwargs.get('slug'))


Using permissions in templates
------------------------------

:file:`templates/base.html`

.. code-block:: html

    {% load permissionsx_tags %}

    {% permissions 'newspaper.profiles.permissions.AuthorPermissions' as user_is_author %}
    {% permissions 'newspaper.profiles.permissions.StaffPermissions' as user_is_staff %}
    {% permissions 'newspaper.profiles.permissions.AdministratorPermissions' as user_is_administrator %}

    <ul id="utility-navigation>
        {% if user_is_administrator %}
            <li><a href="#">Add a new author</a></li>
        {% endif %}
        {% if user_is_staff %}
            <li><a href="#">Publish article</a></li>
        {% endif %}
        {% if user_is_author %}
            <li><a href="#">Write article</a></li>
        {% endif %}
    </ul>


Paid subscription expired, redirect user if trying to access paid content
-------------------------------------------------------------------------

:file:`profiles/models.py`

.. code-block:: python

    import datetime

    from django.db import models


    class Profile(models.Model):

        user = models.OneToOneField('auth.User', max_length=50)
        [...]

        @property
        def is_subscriber(self):
            if self.is_author or self.is_editor or self.is_administrator:
                return True
            if self.date_expires is None:
                return False
            else:
                return datetime.date.today() < self.date_expires


:file:`profiles/permissions.py`

.. code-block:: python

    from permissionsx.models import P
    from permissionsx.models import Permissions

    from newspaper.content.views import SubscriptionExpiredRedirectView


    class SubscriberPermissions(Permissions):

        permissions = P(user__is_authenticated=True) & P(
            user__get_profile__is_subscriber=True, if_false=SubscriptionExpiredRedirectView.as_view()
        )


:file:`content/views.py`

.. code-block:: python

    from django.contrib import messages
    from django.core.urlresolvers import reverse_lazy
    from django.views.generic import DetailView

    from permissionsx.models import P
    from permissionsx.models import Permissions
    from permissionsx.contrib.django import DjangoViewMixin
    from permissionsx.contrib.django import MessageRedirectView

    from newspaper.profiles.permissions import SubscriberPermissions


    class SubscriptionExpiredRedirectView(DjangoViewMixin, MessageRedirectView):

        message = (messages.warning, 'Your subscription has expired!')
        redirect_url = reverse_lazy('subscribe_form')
        permissions_class = Permissions(P(user__is_authenticated=True))


    class ArticleDetailView(DjangoViewMixin, DetailView):

        model = Article
        permissions_class = SubscriberPermissions


    class SongDetailView(DjangoViewMixin, DetailView):

        model = Music
        permissions_class = SubscriberPermissions


    class PictureDetailView(DjangoViewMixin, DetailView):

        model = Picture
        permissions_class = SubscriberPermissions
