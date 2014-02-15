"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import
import copy

from django import template

from permissionsx.contrib.django.helpers import DummyRequest
from permissionsx.utils import get_class


register = template.Library()


@register.assignment_tag(takes_context=True)
def permissions(context, permissions_path, **kwargs):
    """Django template tag for checking permissions inside templates. Usage:
    ::

        {% load permissionsx_tags %}
        {% permissions 'example.profiles.permissions.AuthorPermissions' as user_is_author %}

    """
    module, _, name = permissions_path.rpartition('.')
    permissions = get_class(module, name)
    # NOTE: Dummy request keeps temporary template objects without affecting the real
    #       request. Otherwise iterating over them would change the object that was
    #       assigned at the view level.
    if 'request' in context:
        dummy_request = copy.copy(context['request'])
    else:
        dummy_request = DummyRequest()
        dummy_request.user = context['user']
    try:
        granted = permissions().check(dummy_request, **kwargs)
    except AttributeError:
        # NOTE: AttributeError is _usually_ related to anonymous user being
        #       used for checking permissions.
        # TODO(Robert): Should be reviewed once Django custom user model
        #               gets its anonymous counterpart.
        return False
    return granted
