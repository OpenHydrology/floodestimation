#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Statistical Flood Estimation Tool documentation build configuration file, created by
# sphinx-quickstart on Tue Aug 26 18:45:49 2014.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import os
import sys
from datetime import date
from unittest.mock import MagicMock


# Mock packages that cannot be installed on readthedocs.org.
class Mock(MagicMock):
    @classmethod
    def __getattr__(cls, name):
            return Mock()

MOCK_MODULES = ['numpy', 'numpy.linalg', 'scipy', 'scipy.optimize', 'lmoments3', 'lmoments3.distr']
sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('../../floodestimation'))

# -- General configuration ------------------------------------------------

needs_sphinx = '1.3'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode'
]
source_suffix = '.rst'
master_doc = 'index'

project = 'Flood estimation library'
copyright = '2014‒{}, Open Hydrology contributors'.format(date.today().year)
full_version = open('../../VERSION').read().split('-')[0]  # Ignore build number
version = '.'.join(full_version.split('.')[0:2])
release = full_version
pygments_style = 'sphinx'
autodoc_member_order = 'bysource'
autoclass_content = 'both'

# -- Options for HTML output ----------------------------------------------

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if not on_rtd:  # only import and set the theme if we're building docs locally
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_static_path = ['_static']
html_last_updated_fmt = '%d/%m/%Y'
html_show_sphinx = False
htmlhelp_basename = 'doc'
