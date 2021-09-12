# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['clang_api_doc']

package_data = \
{'': ['*']}

install_requires = \
['clang']

entry_points = \
{'console_scripts': ['clang-api-doc = clang_api_doc.cli:main']}

setup_kwargs = {
    'name': 'clang-api-doc',
    'version': '0.3.0',
    'description': 'Automatically generate API documentation for C language dialects',
    'long_description': "clang-api-doc\n=============================\n\nGenerate C API documentation using libclang Python bindings.\n\nFor an example see the [documentation](https://clang-api-doc.readthedocs.io).\n\n[![CI](https://github.com/GPMueller/clang-api-doc/actions/workflows/ci.yml/badge.svg)](https://github.com/GPMueller/clang-api-doc/actions/workflows/ci.yml)\n[![PyPI version](https://badge.fury.io/py/clang-api-doc.svg)](https://badge.fury.io/py/clang-api-doc)\n\n\nWhy?\n-----------------------------\n\nIdeally, code should be self-documenting. To me that means little to no documentation should be needed in\nthe code itself, as it strongly tends to harm readability if the code already explains itself. The\nremaining use-cases for documentation are typically\n - **API references**, in particular assumed usage contracts\n - usage examples\n - installation instructions\n - general introductions\n\nThis project focuses on generating API references, as the other use-cases tend to be written separate from\nthe code.\n\n\nInstallation\n-----------------------------\n\nThe `clang-api-doc` package is on PyPI, so you can use `pip`, `poetry`, or whatever you like to install it,\nfor example `pip install clang-api-doc`.\n\nTo install it locally and in editable mode, simply install poetry and run `poetry install` and to load the\nvirtual environment run `poetry shell`\n\n\nCLI usage\n-----------------------------\n\nSimply call `clang-api-doc` once per file you wish to document, e.g.\n\n```bash\nclang-api-doc -i 'include/mylib/first.h' -o 'docs/first.md'\nclang-api-doc -i 'include/mylib/second.h' -o 'docs/second.md'\n```\n\nor once per folder, e.g.\n\n```bash\nclang-api-doc -i 'include/mylib/' -o 'docs/'\n```\n\nThese files can then be used in any way you wish to create your final documentation, for example\n- transform to a different format using `pandoc`\n- write an `index.md` file and use `sphinx` to create html docs\n\n\nPython package usage\n-----------------------------\n\n```python\nfrom clang_api_doc import clang_api_doc\n\nfor file_in, file_out in zip(input_files, output_files):\n    clang_api_doc.transform_file(file_in, file_out)\n```",
    'author': 'Gideon Müller',
    'author_email': 'gpmueller@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gpmueller/clang-api-doc',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
