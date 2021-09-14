# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sphinx_rtd_theme

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.ifconfig",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_rtd_theme",
]
source_suffix = [".rst", ".md"]
master_doc = "index"
project = "bkash-client"
year = "2021"
author = "Utsob Roy"
copyright = "{0}, {1}".format(year, author)
version = release = "0.2.2"

pygments_style = "trac"
templates_path = ["."]
extlinks = {
    "issue": ("https://gitlab.com/codesigntheory/python-bkash-client/issues/%s", "#"),
    "pr": ("https://gitlab.com/codesigntheory/python-bkash-client/pull/%s", "PR #"),
}
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
    "githuburl": "https://gitlab.com/codesigntheory/python-bkash-client/"
}

html_use_smartypants = True
html_last_updated_fmt = "%b %d, %Y"
html_split_index = False
html_sidebars = {
    "**": ["searchbox.html", "globaltoc.html", "sourcelink.html"],
}
html_short_title = "%s-%s" % (project, version)

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False
