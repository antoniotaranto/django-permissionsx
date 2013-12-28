# -*- coding: utf-8 -*-

import sys, os

from django.conf import settings

import permissionsx


os.environ['DJANGO_SETTINGS_MODULE'] = 'permissionsx.settings'
settings.configure()
setattr(permissionsx, 'settings', settings)

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.coverage', 'sphinx.ext.viewcode']
templates_path = ['_templates']
source_suffix = '.rst'
source_encoding = 'utf-8-sig'
master_doc = 'index'
project = u'django-permissionsx'
copyright = u'2013-2014, Robert Pogorzelski'
version = permissionsx.__version__
release = version
exclude_patterns = ['_build']
pygments_style = 'sphinx'
html_static_path = ['_static']
html_last_updated_fmt = '%b %d, %Y'
html_show_sourcelink = False
htmlhelp_basename = 'django-permissionsxdoc'
latex_documents = [
  ('index', 'django-permissionsx.tex', u'django-permissionsx Documentation',
   u'Robert Pogorzelski', 'manual'),
]
man_pages = [
    ('index', 'django-permissionsx', u'django-permissionsx Documentation',
     [u'Robert Pogorzelski'], 1)
]
texinfo_documents = [
  ('index', 'django-permissionsx', u'django-permissionsx Documentation',
   u'Robert Pogorzelski', 'django-permissionsx', 'One line description of project.',
   'Miscellaneous'),
]
