"""
PermissionsX - Authorization for Django Class-Based Views.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.utils import importlib


def get_class(module_name, cls_name):
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        raise ImportError('Invalid class path: {}'.format(module_name))
    try:
        cls = getattr(module, cls_name)
    except AttributeError:
        raise ImportError('Invalid class name: {}'.format(cls_name))
    else:
        return cls
