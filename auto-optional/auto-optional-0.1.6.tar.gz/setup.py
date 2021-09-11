# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['auto_optional']

package_data = \
{'': ['*']}

install_requires = \
['libcst>=0.3.20,<0.4.0', 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['auto-optional = auto_optional.main:app']}

setup_kwargs = {
    'name': 'auto-optional',
    'version': '0.1.6',
    'description': 'Makes typed arguments Optional when the default argument is None',
    'long_description': '<img src="https://raw.githubusercontent.com/Luttik/auto-optional/main/docs/assets/images/logo-with-text.svg" style="width: 100%; margin: 32pt 0" alt="Logo">\n\n\n<p align="center">\n    auto-optional: Makes typed arguments Optional when the default argument is None.\n</p>\n\n<p align="center">\n    <a href="https://github.com/Luttik/auto-optional/actions?query=workflow%3ACI+branch%3Amaster">\n        <img src="https://github.com/luttik/auto-optional/workflows/CI/badge.svg" alt="actions batch">\n    </a>\n    <a href="https://pypi.org/project/auto-optional/">\n        <img src="https://badge.fury.io/py/auto-optional.svg" alt="pypi">\n    </a>\n    <a href="https://pypi.org/project/auto-optional/">\n        <img src="https://shields.io/pypi/pyversions/auto-optional" alt="python versions">\n    </a>\n    <a href="https://codecov.io/gh/luttik/auto-optional">\n        <img src="https://codecov.io/gh/Luttik/auto-optional/branch/main/graph/badge.svg" alt="codecov">\n    </a>\n    <a href="https://github.com/Luttik/auto-optional/blob/main/LICENSE">\n        <img src="https://shields.io/github/license/luttik/auto-optional" alt="License: MIT">\n    </a>\n    <a href="https://github.com/psf/black">\n        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">\n    </a>\n</p>\n\n---\n\n**Documentation**: [auto-optional.daanluttik.nl](https://auto-optional.daanluttik.nl)\n\n**Source Code**: [github.com/luttik/auto-optional](https://github.com/Luttik/auto-optional) \n\n---\n\n# What does auto-optional do?\nThe basic purpose of auto-optional is ensuring that whenever a default argument is `None` the type annotation is Optional.\n\nFor example:\n```py\ndef foo(bar: str = None):\n    ...\n```\n\nWould turn into\n\n```py\nfrom typing import Optional\ndef foo(bar: Optional[str] = None):\n    ...\n```\n\n# Why would you want this\n\n- Easily modify external libraries that didn\'t pay attention \n  to proper use of optional to improve mypy linting.\n- Force consistency in your own code-base: \n  Enforcing that `None` parameter implies an `Optional` type. \n\n## Install\nInstall with `pip install auto-optional`.\n\n## Run\nAfter installing you can run auto-optional using `auto-optional [path]` (path is an optional argument).\n\n## Properties\n\n- Existing imports are reused.\n- `import as` statements are properly handled.\n\n## Things of note\n\nFor all these points you can leave a thumbs-up if you want it. Also, I welcome pull-requests for these issues.\n\n- There is no exclude (for file patterns) option yet [[#2]](https://github.com/Luttik/auto-optional/issues/2)\n- There is no ignore (for code lines) option yet [[#3]](https://github.com/Luttik/auto-optional/issues/3)\n- Code is aways read and written as `UTF-8` (which is accurate most of the time). [[#4](https://github.com/Luttik/auto-optional/issues/4)]\n- There is no `diff` or `check` command yet for a dry-run or linting. [[#5](https://github.com/Luttik/auto-optional/issues/5)]\n',
    'author': 'Luttik',
    'author_email': 'dtluttik@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://auto-optional.daanluttik.nl',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>3.7,<4.0',
}


setup(**setup_kwargs)
