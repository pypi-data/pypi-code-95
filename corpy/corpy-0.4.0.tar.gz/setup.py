# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['corpy', 'corpy.morphodita', 'corpy.phonetics', 'corpy.scripts']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'lazy>=1.4,<2.0',
 'lxml>=4.6.1,<5.0.0',
 'numpy>=1.16,<2.0',
 'regex',
 'ufal.morphodita>=1.10,<2.0',
 'ufal.udpipe>=1.2,<2.0',
 'wordcloud>=1.8.1,<2.0.0']

entry_points = \
{'console_scripts': ['xc = corpy.scripts.xc:main',
                     'zip-verticals = corpy.scripts.zip_verticals:main']}

setup_kwargs = {
    'name': 'corpy',
    'version': '0.4.0',
    'description': 'Tools for processing language data.',
    'long_description': "=====\nCorPy\n=====\n\n.. image:: https://readthedocs.org/projects/corpy/badge/?version=stable\n   :target: https://corpy.readthedocs.io/en/stable/?badge=stable\n   :alt: Documentation status\n\n.. image:: https://badge.fury.io/py/corpy.svg\n   :target: https://badge.fury.io/py/corpy\n   :alt: PyPI package\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/python/black\n   :alt: Code style\n\nInstallation\n============\n\n.. code:: bash\n\n   $ python3 -m pip install corpy\n\nOnly recent versions of Python 3 (3.7+) are supported by design.\n\nHelp and feedback\n=================\n\nIf you get stuck, it's always a good idea to start by searching the\ndocumentation, the short URL to which is https://corpy.rtfd.io/.\n\nThe project is developed on GitHub_. You can ask for help via `GitHub\ndiscussions`_ and report bugs and give other kinds of feedback via `GitHub\nissues`_. Support is provided gladly, time and other engagements permitting, but\ncannot be guaranteed.\n\n.. _GitHub: https://github.com/dlukes/corpy\n.. _GitHub discussions: https://github.com/dlukes/corpy/discussions\n.. _GitHub issues: https://github.com/dlukes/corpy/issues\n\nWhat is CorPy?\n==============\n\nA fancy plural for *corpus* ;) Also, a collection of handy but not especially\nmutually integrated tools for dealing with linguistic data. It abstracts away\nfunctionality which is often needed in practice for teaching and/or day to day\nwork at the `Czech National Corpus <https://korpus.cz>`__, without aspiring to\nbe a fully featured or consistent NLP framework.\n\nHere's an idea of what you can do with CorPy:\n\n- add linguistic annotation to raw textual data using either `UDPipe\n  <https://corpy.rtfd.io/en/stable/guides/udpipe.html>`__ or `MorphoDiTa\n  <https://corpy.rtfd.io/en/stable/guides/morphodita.html>`__\n- `easily generate word clouds\n  <https://corpy.rtfd.io/en/stable/guides/vis.html>`__\n- run code in `a sanitized global environment\n  <https://corpy.rtfd.io/en/stable/guides/clean_env.html>`__ (useful for\n  debugging in interactive sessions, e.g. with Jupyter notebooks in `JupyterLab\n  <https://jupyterlab.rtfd.io>`__)\n- `generate phonetic transcripts of Czech texts\n  <https://corpy.rtfd.io/en/stable/guides/phonetics_cs.html>`__\n- `wrangle corpora in the vertical format\n  <https://corpy.rtfd.io/en/stable/guides/vertical.html>`__ devised originally\n  for `CWB <http://cwb.sourceforge.net/>`__, used also by `(No)SketchEngine\n  <https://nlp.fi.muni.cz/trac/noske/>`__\n- plus some `command line utilities\n  <https://corpy.rtfd.io/en/stable/guides/cli.html>`__\n\n.. note::\n\n   **Should I pick UDPipe or MorphoDiTa?**\n\n   Both are developed at `ÚFAL MFF UK`_. UDPipe_ has more features at the cost\n   of being somewhat more complex: it does both `morphological tagging\n   (including lemmatization) and syntactic parsing\n   <https://corpy.rtfd.io/en/stable/guides/udpipe.html>`__, and it handles a\n   number of different input and output formats. You can also download\n   `pre-trained models <http://ufal.mff.cuni.cz/udpipe/models>`__ for many\n   different languages.\n\n   By contrast, MorphoDiTa_ only has `pre-trained models for Czech and English\n   <http://ufal.mff.cuni.cz/morphodita/users-manual>`__, and only performs\n   `morphological tagging (including lemmatization)\n   <https://corpy.rtfd.io/en/stable/guides/morphodita.html>`__. However, its\n   output is more straightforward -- it just splits your text into tokens and\n   annotates them, whereas UDPipe can (depending on the model) introduce\n   additional tokens necessary for a more explicit analysis, add multi-word\n   tokens etc. This is because UDPipe is tailored to the type of linguistic\n   analysis conducted within the UniversalDependencies_ project, using the\n   CoNLL-U_ data format.\n\n   MorphoDiTa can also help you if you just want to tokenize text and don't have\n   a language model available.\n\n.. _`ÚFAL MFF UK`: https://ufal.mff.cuni.cz/\n.. _UDPipe: https://ufal.mff.cuni.cz/udpipe\n.. _MorphoDiTa: https://ufal.mff.cuni.cz/morphodita\n.. _UniversalDependencies: https://universaldependencies.org\n.. _CoNLL-U: https://universaldependencies.org/format.html\n\n.. development-marker\n\nDevelopment\n===========\n\nDependencies and building the docs\n----------------------------------\n\n``corpy`` needs to be installed in the ReadTheDocs virtualenv for ``autodoc`` to\nwork. That's configured in ``.readthedocs.yml``. However, ``pip`` doesn't\ninstall ``[tool.poetry.dev-dependencies]``, which contain the Sphinx version and\ntheme we're using. Maybe there's a way of forcing that, but we probably don't\nwant to anyway -- it's a waste of time to install linters, testing frameworks\netc. that won't be used. So instead, we have a ``docs/requirements.txt`` file\nmanaged by ``check.sh`` which only contains Sphinx + the theme, and which we\nspecify via ``.readthedocs.yml``.\n\n.. license-marker\n\nLicense\n=======\n\nCopyright © 2016--present `ÚČNK <http://korpus.cz>`__/David Lukeš\n\nDistributed under the `GNU General Public License v3\n<http://www.gnu.org/licenses/gpl-3.0.en.html>`__.\n",
    'author': 'David Lukes',
    'author_email': 'dafydd.lukes@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dlukes/corpy',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
