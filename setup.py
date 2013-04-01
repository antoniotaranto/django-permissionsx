"""
PermissionsX - Authorization for Django Class-Based Views.

:copyright: Copyright (c) 2013 by Robert Pogorzelski.
:license:   BSD, see LICENSE for more details.

"""
import sys

from setuptools import setup
from setuptools import find_packages

version = __import__('permissionsx').__version__

setup(
    name='django-permissionsx',
    version=version,
    description='Authorization for Django Class-Based Views.',
    author='Robert Pogorzelski',
    author_email='thinkingpotato@gmail.com',
    url='http://github.com/thinkingpotato/django-permissionsx',
    license='BSD',
    platforms=['OS Independent'],
    packages=find_packages(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
    ],
    install_requires=['Django>=1.4.5'],
    test_suite='runtests',
)
