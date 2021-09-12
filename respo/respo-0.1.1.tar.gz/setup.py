# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['respo']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'colorama>=0.4.4,<0.5.0',
 'pydantic>=1.8.2,<2.0.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['respo = respo.typer:app']}

setup_kwargs = {
    'name': 'respo',
    'version': '0.1.1',
    'description': 'File based RBAC in Python made easy',
    'long_description': '<a href="https://codecov.io/gh/rafsaf/respo" target="_blank">\n  <img src="https://img.shields.io/codecov/c/github/rafsaf/respo" alt="Coverage">\n</a>\n\n<a href="https://github.com/rafsaf/respo/actions?query=workflow%3ATest" target="_blank">\n    <img src="https://github.com/rafsaf/respo/workflows/Test/badge.svg" alt="Test">\n</a>\n\n<a href="https://github.com/rafsaf/respo/actions?query=workflow%3APublish" target="_blank">\n  <img src="https://github.com/rafsaf/respo/workflows/Publish/badge.svg" alt="Publish">\n</a>\n\n<a href="https://github.com/rafsaf/respo/blob/main/LICENSE" target="_blank">\n    <img src="https://img.shields.io/github/license/rafsaf/respo" alt="License">\n</a>\n\n<a href="https://pypi.org/project/respo/" target="_blank">\n    <img src="https://img.shields.io/pypi/pyversions/respo" alt="Python version">\n</a>\n\n## File based RBAC in Python made easy\n\n### Under development\n',
    'author': 'rafsaf',
    'author_email': 'rafal.safin@rafsaf.pl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rafsaf/respo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
