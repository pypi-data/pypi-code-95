# -*- coding: utf-8 -*-
# GENOCIDE - using the law to administer poison the king commits genocide
#
# OTP-CR-117/19/001 | otp.informationdesk@icc-cpi.int | https://genocide.rtfd.io

import doctest, os, sys, unittest

curdir = os.getcwd()
sys.path.insert(0, curdir + os.sep)
sys.path.insert(0, curdir + os.sep + ".." + os.sep + "gcd")

# -- Options for GENERIC output ---------------------------------------------

__version__ = 36

project = "genocide"
master_doc = 'index'
version = '%s' % __version__
release = '%s' % __version__
language = ''
today = ''
today_fmt = '%B %d, %Y'
needs_sphinx='1.7'
exclude_patterns = ['_build', '_templates', '_source', 'Thumbs.db', '.DS_Store']
source_suffix = '.rst'
source_encoding = 'utf-8-sig'
modindex_common_prefix = [""]
keep_warnings = True
templates_path=['_templates']
add_function_parentheses = True
add_module_names = False
show_authors = False
pygments_style = 'sphinx'

extensions=[
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx.ext.githubpages',
    #'sphinx_autodoc_annotation'
]

# -- Options for HTML output -------------------------------------------------

html_theme = "haiku"
html_title = "GENOCIDE %s" % __version__
html_short_title = ""
html_favicon = "genocide3smile.png"
html_extra_path = []
html_last_updated_fmt = '%Y-%b-%d'
html_additional_pages = {}
html_domain_indices = False
html_use_index = False
html_split_index = False
html_show_sourcelink = False
html_show_sphinx = False
html_show_copyright = False
html_copy_source = False
html_use_opensearch = 'http://genocide.rtfd.io/'
html_file_suffix = '.html'
htmlhelp_basename = 'testdoc'

rst_prolog = """.. image:: genocide3line.png
    :height: 2.6cm
    :width: 100%
"""

intersphinx_mapping = {
                       'python': ('https://docs.python.org/3', 'objects.inv'),
                       'sphinx': ('http://sphinx.pocoo.org/', None),
                      }
intersphinx_cache_limit=1

# -- Options for CODE output -------------------------------------------------

autosummary_generate=True
autodoc_default_flags=['members', 'undoc-members', 'private-members', "imported-members"]
#autodoc_member_order='alphabetical'
autodoc_member_order='groupwise'
autodoc_docstring_signature=True
autoclass_content="class"
doctest_global_setup=""
doctest_global_cleanup=""
doctest_test_doctest_blocks="default"
trim_doctest_flags=True
doctest_flags=doctest.REPORT_UDIFF
nitpick_ignore=[
                ('py:class', 'builtins.BaseException'),
               ]
