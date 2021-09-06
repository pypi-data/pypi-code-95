# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['_delb', '_delb.plugins', 'delb']

package_data = \
{'': ['*']}

install_requires = \
['cssselect', 'lxml', 'setuptools']

extras_require = \
{'https-loader': ['requests>=2.21,<3.0']}

entry_points = \
{'delb': ['https-loader = _delb.plugins.https_loader']}

setup_kwargs = {
    'name': 'delb',
    'version': '0.3b4',
    'description': 'A library that provides an ergonomic model for XML encoded text documents (e.g. with TEI-XML).',
    'long_description': "delb\n====\n\n|latest-version| |rtd| |python-support| |license| |black|\n\n``delb`` is a library that provides an ergonomic model for XML encoded text\ndocuments (e.g. TEI-XML_) for the Python programming language.\nIt fills a gap for the humanities-related field of software development towards\nthe excellent (scientific) communities in the Python ecosystem.\n\nFor a more elaborated discussion see the *Design* chapter of the documentation.\n\n.. _TEI-XML: https://tei-c.org\n\n\nFeatures\n--------\n\n- Loads documents from various source types. This is customizable and\n  extensible.\n- XML DOM types are represented by distinct classes.\n- A completely type-annotated API.\n- Consistent design regarding names and callables' signatures.\n- Shadows comments and processing instructions by default.\n- Querying with XPath and CSS expressions.\n- Applying XSL Transformations.\n\n\nDevelopment status\n------------------\n\nYou're invited to submit tests that reflect desired use cases or are merely of\ntheoretical nature. Of course, any kind of proposals for or implementations of\nimprovements are welcome as well.\n\n\nRelated Projects & Testimonials\n-------------------------------\n\nsnakesist_ is an eXist-db client that uses ``delb`` to expose database\nresources.\n\nKurt Raschke `noted in 2010`_::\n\n  In a DOM-based implementation, it would be relatively easy […]\n  But lxml doesn't use text nodes; instead it uses and properties to hold text\n  content.\n\n\n.. _snakesist: https://pypi.org/project/snakesist/\n.. _noted in 2010: https://web.archive.org/web/20190316214219/https://kurtraschke.com/2010/09/lxml-inserting-elements-in-text/\n\nROADMAPish\n----------\n\n- gain insights from usage experience\n- implement the API in Rust\n- provide bindings for Python and Javascript to the Rust implementation, while\n  nurturing the lxml-based implementation as reference for some time\n- be finished before the Digital Humanities community realizes how to foster a\n  viable software ecosystem and fund such efforts\n\n\n.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square\n   :alt: Black code style\n   :target: https://black.readthedocs.io/\n.. |latest-version| image:: https://img.shields.io/pypi/v/delb.svg?style=flat-square\n   :alt: Latest version on PyPI\n   :target: https://pypi.org/project/delb\n.. |license| image:: https://img.shields.io/pypi/l/delb.svg?style=flat-square\n   :alt: License\n   :target: https://github.com/funkyfuture/delb/blob/main/LICENSE.txt\n.. |python-support| image:: https://img.shields.io/pypi/pyversions/delb.svg?style=flat-square\n   :alt: Python versions\n.. |rtd| image:: https://img.shields.io/badge/RTD-Docs-informational.svg?style=flat-square\n   :alt: Documentation\n   :target: https://delb.readthedocs.io/\n",
    'author': 'Frank Sachsenheim',
    'author_email': 'funkyfuture@riseup.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/funkyfuture/delb',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
