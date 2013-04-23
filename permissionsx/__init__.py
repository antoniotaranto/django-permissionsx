"""
PermissionsX - Authorization for Django Class-Based Views.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
import os
import sys

VERSION = (0, 0, 5)

__version__ = ".".join(map(str, VERSION[0:3])) + "".join(VERSION[3:])
__author__ = "Robert Pogorzelski <thinkingpotato@gmail.com>"
__docformat__ = "restructuredtext"

if sys.version_info < (2, 7):
    import warnings
    warnings.warn(DeprecationWarning("""

Only version 2.7 of Python is currently supported.

"""))