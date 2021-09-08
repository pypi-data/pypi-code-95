# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pybomb', 'pybomb.clients', 'pybomb.clients.base']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.19.0,<3.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata>=1.7.0,<2.0.0']}

setup_kwargs = {
    'name': 'pybomb',
    'version': '0.3.0',
    'description': 'Simple clients for the Giant Bomb API.',
    'long_description': "[![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/C0C826VYD)\n\n![Tests](https://github.com/steveYeah/PyBomb/workflows/Tests/badge.svg)\n![Coverage](https://github.com/steveYeah/PyBomb/workflows/Coverage/badge.svg)\n![Release Drafter](https://github.com/steveYeah/PyBomb/workflows/Release%20Drafter/badge.svg)\n![TestPyPi](https://github.com/steveYeah/PyBomb/workflows/TestPyPi/badge.svg)\n![Release](https://github.com/steveYeah/PyBomb/workflows/Release/badge.svg)\n\n[![Codecov](https://codecov.io/gh/steveYeah/PyBomb/branch/master/graph/badge.svg)](https://codecov.io/gh/steveYeah/PyBomb)\n[![PyPI](https://img.shields.io/pypi/v/PyBomb.svg)](https://pypi.org/project/PyBomb/)\n[![Read the Docs](https://readthedocs.org/projects/pybomb/badge/)](https://pybomb.readthedocs.io/)\n\n# PyBomb\n\n>\n\nThis will go into version 1.0 when all resources are supported.\n\n**Currently Supported Resources**:\n\n  - games\n  - game\n  - platforms\n\n## Support OSS, and me :)\nIf you find this project useful, please feel free to [buy me a coffee](https://ko-fi.com/steveyeah)\n\n## Install\n\n``` shell\npip install pybomb\n```\n\n## Examples\n\nTo see a working example of Pybomb, take a look at the example project\n[PyBomb-demo](https://github.com/steveYeah/PyBomb-demo)\n\n**GamesClient - search**\n\n    import pybomb\n\n    my_key = your_giant_bomb_api_key\n    games_client = pybomb.GamesClient(my_key)\n\n    return_fields = ('id', 'name', 'platforms')\n    limit = 10\n    offset = 5\n    sort_by = 'name'\n    filter_by = {'platforms': pybomb.PS3}\n\n    response = games_client.search(\n       filter_by=filter_by,\n       return_fields=return_fields,\n       sort_by=sort_by,\n       desc=True,\n       limit=limit,\n       offset=offset\n    )\n\n    print response.results\n    print response.uri\n    print response.num_page_results\n    print response.num_total_results\n\n**GamesClient - quick\\_search**\n\n    import pybomb\n\n    my_key = your_giant_bomb_api_key\n    games_client = pybomb.GamesClient(my_key)\n\n    response = games_client.quick_search(\n      name='call of duty',\n      platform=pybomb.PS3,\n      sort_by='original_release_date',\n      desc=True\n    )\n\n    print response.results\n    print response.uri\n    print response.num_page_results\n    print response.num_total_results\n\n## Documentation\n\nThe full documentation, including more examples can be found at\n[readthedocs](https://pybomb.readthedocs.org)\n\n## Contributing\n\nThis project uses [Poetry](https://python-poetry.org/) and [Nox](https://nox.thea.codes/en/stable/) so make sure you have those setup!\n\nWhilst working you can use\n\n```shell\n$ nox -rs tests\n```\nto run the tests, but once you have finished, make sure to run all of nox before making a PR\n\n```shell\n$ nox\n```\n\nThis project also uses [Pytest](https://docs.pytest.org/en/stable/) for tests, and we aim for 100% test coverage. The build will fail when the coverage is less than this, but feel free to use `# pragma: no cover` if it makes sense to do so (although this should be very rare). [Mypy](http://mypy-lang.org/) is also used, and we even use [typeguard](https://typeguard.readthedocs.io/en/latest/) so typing is important here!\n\nI am always happy to help where I can and I try to be as responsive as possible to PRs. Email me if I am slow, or if you need any help!\n",
    'author': 'steveYeah',
    'author_email': 'hutchinsteve@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/steveYeah/PyBomb',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
