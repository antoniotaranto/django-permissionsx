"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from debug_toolbar.panels import DebugPanel
from debug_toolbar.utils import get_name_from_obj

from permissionsx.utils import get_class


class PermissionsDebugPanel(DebugPanel):

    name = 'PermissionsX'
    template = 'permissionsx/panels/permissionsx.html'
    has_content = True

    def __init__(self, *args, **kwargs):
        super(PermissionsDebugPanel, self).__init__(*args, **kwargs)
        self._views_cache = {}

    def nav_title(self):
        return _('Permissions')

    def title(self):
        return _('Permissions')

    def url(self):
        return ''

    def process_request(self, request):
        self.request = request

    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            view = get_class(view_func.__module__, view_func.__name__)
        except ImportError:
            # NOTE: This could be caused by wrapping view.
            return

        view_info = {
             'view_name': _('<no view>'),
             'view_permissions': _('Not defined'),
             'view_rules': _('Not defined'),
         }
        try:
            view_info['view_name'] = get_name_from_obj(view)
            try:
                view_info['view_permissions'] = get_name_from_obj(view.permissions_class)
                view_info['view_rules'] = view.permissions_class().get_permissions(request)
            except AttributeError:
                # NOTE: No permissions defined for this view.
                pass
        except Http404:
            pass
        self.record_stats(view_info)
