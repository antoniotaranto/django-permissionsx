"""PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

from django.utils import importlib


def get_class(module_name, cls_name):
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        raise ImportError('Cannot import class "{0}"'.format('.'.join((module_name, cls_name))))
    try:
        cls = getattr(module, cls_name)
    except AttributeError:
        raise ImportError('Class "{0}" not found in {1}'.format(cls_name, module_name))
    else:
        return cls
