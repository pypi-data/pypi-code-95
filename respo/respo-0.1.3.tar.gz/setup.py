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
    'version': '0.1.3',
    'description': 'File based RBAC in Python made easy',
    'long_description': '<a href="https://codecov.io/gh/rafsaf/respo" target="_blank">\n  <img src="https://img.shields.io/codecov/c/github/rafsaf/respo" alt="Coverage">\n</a>\n\n<a href="https://github.com/rafsaf/respo/actions?query=workflow%3ATest" target="_blank">\n    <img src="https://github.com/rafsaf/respo/workflows/Test/badge.svg" alt="Test">\n</a>\n\n<a href="https://github.com/rafsaf/respo/actions?query=workflow%3APublish" target="_blank">\n  <img src="https://github.com/rafsaf/respo/workflows/Publish/badge.svg" alt="Publish">\n</a>\n\n<a href="https://github.com/rafsaf/respo/actions?query=workflow%3AGh-Pages" target="_blank">\n  <img src="https://github.com/rafsaf/respo/workflows/Gh-Pages/badge.svg" alt="Gh-Pages">\n</a>\n\n<a href="https://github.com/rafsaf/respo/blob/main/LICENSE" target="_blank">\n    <img src="https://img.shields.io/github/license/rafsaf/respo" alt="License">\n</a>\n\n<a href="https://pypi.org/project/respo/" target="_blank">\n    <img src="https://img.shields.io/pypi/pyversions/respo" alt="Python version">\n</a>\n\n# Documentation\n\n**https://rafsaf.github.io/respo/**\n\n# Overview\n\n_respo_ states for **Resource Policy** and is tiny, user friendly tool for building RBAC systems based on single `yml` file, mainly with FastAPI framework in mind. In most cases – for even large set of roles and organizations – single file would be enough to provide restricting system access.\n\n# Installation\n\n```\npip install respo\n```\n\n# Tests in this project\n\nThis project focuses heavily on code quality, good practics and full 100% test coverage\n\nAlso, every piece of code in the docs is a tested python/yml file, feel free to use it directly.\n',
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
