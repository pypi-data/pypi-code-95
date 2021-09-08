# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../"))

# -- Project information -----------------------------------------------------

project = "xotless"
author = "Merchise Autrement"

from datetime import datetime  # noqa

# Any year before to 2012 xoutil copyrights to "Medardo Rodriguez"
copyright = f"2012-{datetime.now().year} {author} [~º/~] and Contributors"
del datetime


# The full version, including alpha/beta/rc tags
try:
    from xotless.release import VERSION
except ImportError:

    def up(path, level=1):
        result = path
        while level:
            result = os.path.dirname(result)
            level -= 1
        return result

    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _project_dir = os.path.abspath(os.path.join(up(_current_dir, 2)))
    sys.path.append(_project_dir)
    from xotless.release import VERSION
version = VERSION[: VERSION.rfind(".")]

try:
    from xotless.release import RELEASE_TAG

    release = VERSION
    if RELEASE_TAG:
        release += RELEASE_TAG
except:
    # The full version, including alpha/beta/rc tags.
    release = VERSION


# -- General configuration ---------------------------------------------------

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = ".rst"

# The encoding of source files.
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = "index"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
try:
    import sphinx_rtd_theme

    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
except ImportError:
    html_theme = "pyramid"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


# Configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "py3": ("https://docs.python.org/3.8/", None),
    "hypothesis": ("https://hypothesis.readthedocs.io/en/latest/", None),
    "xotl.tools": ("https://xoutil.readthedocs.io/en/latest/", None),
}

# Maintain the cache forever.
intersphinx_cache_limit = 365

autosummary_generate = True

# Produce output for todo and todolist
todo_include_todos = True
