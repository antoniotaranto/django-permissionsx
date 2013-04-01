"""
PermissionsX - Authorization for Django Class-Based Views.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from django.utils import importlib


def get_class(*args):
    if len(args) == 1:
        module_path, _, class_name = args[0].rpartition('.')
    elif len(args) == 2:
        module_path, class_name = args
    else:
        raise Exception('{} is invalid get_class() parameter')
    try:
        module = importlib.import_module(module_path)
    except ImportError:
        raise ImportError('Invalid class path: {}'.format(module_path))
    try:
        cls = getattr(module, class_name)
    except AttributeError:
        raise ImportError('Invalid class name: {}'.format(class_name))
    else:
        return cls