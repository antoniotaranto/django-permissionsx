#!/usr/bin/env python
"""
PermissionsX - Authorization for Django.

:copyright: Copyright (c) 2013-2014 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
from __future__ import absolute_import
import sys

from setuptools.command.test import test as TestCommand
from setuptools import find_packages
from setuptools import setup


version = __import__('permissionsx').__version__


class Tox(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


setup(
    name='django-permissionsx',
    version=version,
    description='Authorization for Django.',
    author='Robert Pogorzelski',
    author_email='thinkingpotato@gmail.com',
    url='http://github.com/thinkingpotato/django-permissionsx',
    license='BSD',
    platforms=['OS Independent'],
    packages=find_packages(),
    package_data={str('permissionsx'): [str('templates/permissionsx/panels/*')]},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
    ],
    tests_require=['tox'],
    cmdclass={'test': Tox},
)
