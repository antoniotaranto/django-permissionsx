"""
PermissionsX - Authorization for Django.

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
    description='Authorization for Django.',
    author='Robert Pogorzelski',
    author_email='thinkingpotato@gmail.com',
    url='http://github.com/thinkingpotato/django-permissionsx',
    license='BSD',
    platforms=['OS Independent'],
    packages=find_packages(),
    package_data={str('permissionsx'): [str('templates/permissionsx/panels/*')]},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
    ],
    install_requires=[
        'django-classy-tags >= 0.4',
    ],
)
