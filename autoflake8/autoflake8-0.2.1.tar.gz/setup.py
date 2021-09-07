# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autoflake8']

package_data = \
{'': ['*']}

install_requires = \
['pyflakes>=2.3.0']

entry_points = \
{'console_scripts': ['autoflake8 = autoflake8.cli:main']}

setup_kwargs = {
    'name': 'autoflake8',
    'version': '0.2.1',
    'description': 'Tool to automatically fix some issues reported by flake8 (forked from autoflake).',
    'long_description': "# autoflake8\n\n[![Build](https://github.com/fsouza/autoflake8/actions/workflows/main.yaml/badge.svg?branch=main)](https://github.com/fsouza/autoflake8/actions/workflows/main.yaml)\n\n## Introduction\n\n*autoflake8* removes unused imports and unused variables from Python code. It\nmakes use of [pyflakes](https://pypi.org/project/pyflakes/) to do this.\n\nautoflake8 also removes useless ``pass`` statements.\n\nIt's a maintained fork of [autoflake](https://github.com/myint/autoflake).\n\n## Differences from autoflake\n\nThis fork of autoflake removed some features from autoflake and modified\ncertain behaviors. The main motivations for those changes is the idea that\nautoflake8 is built for users of flake8 and it's assumed that if you're using\nautoflake8, you're also using flake8. This motivated the removal of the flags\n`--imports` and `--remove-all-unused-imports`: if you want to preserve an\nimport for its side-effect, use `# noqa`.\n\nAdditionally, `autoflake8` also supports load from `stdin` and printing to\n`stdout`, which makes it very easy for users to integrate with their custom\neditors.\n\nFinally, a big difference is that `autoflake8` exits with status 1 when it\ndetects issues/rewrite files. For editor integration, the new flag\n`--exit-zero-even-if-changed` can be used. When that flag is defined,\n`autoflake8` will return status 0 even when it modifies files.\n\nIn terms of future plans, we also plan to eventually stop using regular\nexpressions and rely on actual AST rewriting to fix issues reported by flake8.\n\n## Example\n\nRunning autoflake8 on the below example::\n\n```\n$ autoflake8 --in-place --remove-unused-variables example.py\n```\n\n```python\nimport math\nimport re\nimport os\nimport random\nimport multiprocessing\nimport grp, pwd, platform\nimport subprocess, sys\n\n\ndef foo():\n    from abc import ABCMeta, WeakSet\n    try:\n        import multiprocessing\n        print(multiprocessing.cpu_count())\n    except ImportError as exception:\n        print(sys.version)\n    return math.pi\n```\n\nResults in:\n\n```python\nimport math\nimport sys\n\n\ndef foo():\n    try:\n        import multiprocessing\n        print(multiprocessing.cpu_count())\n    except ImportError:\n        print(sys.version)\n    return math.pi\n```\n\n## Installation\n\n```\n$ pip install --upgrade autoflake8\n```\n\n## Using as a pre-commit hook\n\n`autoflake8` can be used as a pre-commit hook. See\n[pre-commit](https://pre-commit.com/#plugins) for instructions.\n\nSample `.pre-commit-config.yaml`:\n\n```yaml\n-   repo: https://github.com/fsouza/autoflake8\n    rev: v0.2.1\n    hooks:\n    -   id: autoflake8\n```\n\n## Advanced usage\n\nTo remove unused variables, use the ``--remove-unused-variables`` option.\n\nBelow is the full listing of options::\n\n```\nusage: autoflake8 [-h] [-c] [-r] [--exclude globs] [--expand-star-imports] [--remove-duplicate-keys] [--remove-unused-variables] [--version] [-v] [--exit-zero-even-if-changed] [-i | -s] files [files ...]\n\npositional arguments:\n  files                 files to format\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -c, --check           return error code if changes are needed\n  -r, --recursive       drill down directories recursively\n  --exclude globs       exclude file/directory names that match these comma-separated globs\n  --expand-star-imports\n                        expand wildcard star imports with undefined names; this only triggers if there is only one star import in the file; this is skipped if there are any uses of `__all__` or `del` in the file\n  --remove-duplicate-keys\n                        remove all duplicate keys in objects\n  --remove-unused-variables\n                        remove unused variables\n  --version             show program's version number and exit\n  -v, --verbose         print more verbose logs (you can repeat `-v` to make it more verbose)\n  --exit-zero-even-if-changed\n  -i, --in-place        make changes to files instead of printing diffs\n  -s, --stdout          print changed text to stdout. defaults to true when formatting stdin, or to false otherwise\n```\n\n\n### Tests\n\nTo run the unit tests::\n\n```\n$ poetry run pytest\n```\n\nThere is also a fuzz test, which runs against any collection of given Python\nfiles. It tests autoflake8 against the files and checks how well it does by\nrunning pyflakes on the file before and after. The test fails if the pyflakes\nresults change for the worse. (This is done in memory. The actual files are\nleft untouched.)::\n\n```\n$ poetry run scripts/test_fuzz.py\n```\n\n## Excluding specific lines\n\nIt might be the case that you have some imports for their side effects, even\nif you are not using them directly in that file.\n\nThat is common, for example, in Flask based applications. In where you import\nPython modules (files) that imported a main ``app``, to have them included in\nthe routes.\n\nFor example:\n\n```python\nfrom .endpoints import role, token, user, utils\n```\n\nTo prevent that, without having to exclude the entire file, you can add a\n``# noqa`` comment at the end of the line, like:\n\n```python\nfrom .endpoints import role, token, user, utils  # noqa\n```\n\nThat line will instruct ``autoflake8`` to let that specific line as is.\n",
    'author': 'Francisco Souza',
    'author_email': 'fsouza@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fsouza/autoflake8',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
