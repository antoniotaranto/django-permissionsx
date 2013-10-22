"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.utils import importlib


def get_class(module_name, cls_name):
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        raise ImportError('Cannot import class "{}"'.format('.'.join((module_name, cls_name))))
    try:
        cls = getattr(module, cls_name)
    except AttributeError:
        raise ImportError('Class "{}" not found in {}'.format(cls_name, module_name))
    else:
        return cls
