# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mail_deduplicate', 'mail_deduplicate.tests']

package_data = \
{'': ['*']}

install_requires = \
['arrow>=0.17,<1.2',
 'boltons>=20.2.1,<22.0.0',
 'click-help-colors>=0.8,<0.10',
 'click-log>=0.3.2,<0.4.0',
 'click>=8.0.0,<9.0.0',
 'tabulate>=0.8.7,<0.9.0',
 'tomlkit>=0.7.0,<0.8.0']

extras_require = \
{'docs': ['sphinx>=3.4.2,<5.0.0', 'sphinx_rtd_theme>=0.5.1,<0.6.0']}

entry_points = \
{'console_scripts': ['mdedup = mail_deduplicate.cli:mdedup']}

setup_kwargs = {
    'name': 'mail-deduplicate',
    'version': '6.2.0',
    'description': '📧 CLI to deduplicate mails from mail boxes.',
    'long_description': 'Mail Deduplicate\n================\n\nCommand-line tool to deduplicate mails from a set of boxes.\n\nStable release: |release| |versions|\n\nDevelopment: |build| |docs| |coverage|\n\n.. |release| image:: https://img.shields.io/pypi/v/mail-deduplicate.svg\n    :target: https://pypi.python.org/pypi/mail-deduplicate\n    :alt: Last release\n.. |versions| image:: https://img.shields.io/pypi/pyversions/mail-deduplicate.svg\n    :target: https://pypi.python.org/pypi/mail-deduplicate\n    :alt: Python versions\n.. |build| image:: https://github.com/kdeldycke/mail-deduplicate/workflows/Tests/badge.svg\n    :target: https://github.com/kdeldycke/mail-deduplicate/actions?query=workflow%3ATests\n    :alt: Unittests status\n.. |docs| image:: https://readthedocs.org/projects/mail-deduplicate/badge/?version=develop\n    :target: https://mail-deduplicate.readthedocs.io/en/develop/\n    :alt: Documentation Status\n.. |coverage| image:: https://codecov.io/gh/kdeldycke/mail-deduplicate/branch/develop/graph/badge.svg\n    :target: https://codecov.io/github/kdeldycke/mail-deduplicate?branch=develop\n    :alt: Coverage Status\n\n.. figure:: https://raw.githubusercontent.com/kdeldycke/mail-deduplicate/develop/docs/cli-coloured-header.png\n    :align: center\n\n\nFeatures\n--------\n\n* Duplicate detection based on cherry-picked and normalized mail headers.\n* Source and deduplicate mails from multiple sources.\n* Reads and writes to ``mbox``, ``maildir``, ``babyl``, ``mh`` and ``mmdf`` formats.\n* Multiple duplicate selection strategies based on size, content, timestamp, file\n  path or random choice.\n* Copy, move or delete the resulting set of mails after the deduplication.\n* Dry-run mode.\n* Protection against false-positives by checking for size and content\n  differences.\n\n\nScreenshots\n-----------\n\n.. figure:: https://raw.githubusercontent.com/kdeldycke/mail-deduplicate/develop/docs/cli-colored-help.png\n    :align: center\n\n.. figure:: https://raw.githubusercontent.com/kdeldycke/mail-deduplicate/develop/docs/cli-coloured-run.png\n    :align: center\n\n\nInstallation\n------------\n\nThis package is `available on PyPi\n<https://pypi.python.org/pypi/mail-deduplicate>`_, so you can install the\nlatest stable release and its dependencies with a simple ``pip`` call:\n\n.. code-block:: shell-session\n\n    $ pip install mail-deduplicate\n\n\nDocumentation\n-------------\n\nDocs are `hosted on Read the Docs\n<https://mail-deduplicate.readthedocs.io>`_.\n',
    'author': 'Kevin Deldycke',
    'author_email': 'kevin@deldycke.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kdeldycke/mail-deduplicate',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
