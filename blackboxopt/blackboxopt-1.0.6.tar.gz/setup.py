# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['blackboxopt',
 'blackboxopt.examples',
 'blackboxopt.optimization_loops',
 'blackboxopt.optimizers',
 'blackboxopt.optimizers.staged',
 'blackboxopt.visualizations']

package_data = \
{'': ['*']}

install_requires = \
['parameterspace>=0.7.2,<0.8.0']

extras_require = \
{'all': ['numpy>=1.20.1,<2.0.0',
         'plotly>=4.14.3,<5.0.0',
         'scipy>=1.6.0,<2.0.0',
         'statsmodels>=0.12.2,<0.13.0',
         'dask>=2021.2.0,<2022.0.0',
         'distributed>=2021.2.0,<2022.0.0',
         'pandas>=1.2.4,<2.0.0'],
 'bohb': ['numpy>=1.20.1,<2.0.0',
          'scipy>=1.6.0,<2.0.0',
          'statsmodels>=0.12.2,<0.13.0'],
 'dask': ['dask>=2021.2.0,<2022.0.0', 'distributed>=2021.2.0,<2022.0.0'],
 'hyperband': ['numpy>=1.20.1,<2.0.0'],
 'testing': ['numpy>=1.20.1,<2.0.0'],
 'visualization': ['plotly>=4.14.3,<5.0.0',
                   'scipy>=1.6.0,<2.0.0',
                   'pandas>=1.2.4,<2.0.0']}

setup_kwargs = {
    'name': 'blackboxopt',
    'version': '1.0.6',
    'description': 'A common interface for blackbox optimization algorithms along with useful helpers like parallel optimization loops, analysis and visualization scripts.',
    'long_description': '# Blackbox Optimization\n\nVarious blackbox optimization algorithms with a common interface along with useful\nhelpers like parallel optimization loops, analysis and visualization scripts.\n\nRandom search is provided as an example optimizer along with tests for the interface.\n\nNew optimizers can require `blackboxopt` as a dependency, which is just the light-weight\ninterface definition.\nIf you want all optimizer implementations that come with this package, install\n`blackboxopt[all]`\nAlternatively, you can get individual optimizers with e.g. `blackboxopt[bohb]`\n\nThis software is a research prototype.\nThe software is not ready for production use.\nIt has neither been developed nor tested for a specific use case.\nHowever, the license conditions of the applicable Open Source licenses allow you to\nadapt the software to your needs.\nBefore using it in a safety relevant setting, make sure that the software fulfills your\nrequirements and adjust it according to any applicable safety standards\n(e.g. ISO 26262).\n\n## Documentation\n\n**Visit [boschresearch.github.io/blackboxopt](https://boschresearch.github.io/blackboxopt/)**\n\n## Development\n\nInstall poetry\n\n```\npip install poetry\n```\n\nInstall the `blackboxopt` package from source by running the following from the root\ndirectory of _this_ repository\n\n```\npoetry install\n```\n\n(Optional) Install [pre-commit](https://pre-commit.com) hooks to check code standards\nbefore committing changes:\n\n```\npoetry run pre-commit install\n```\n\n## Test\n\nMake sure to install all extras before running tests\n\n```\npoetry install -E testing\npoetry run pytest tests/\n```\n\nFor HTML test coverage reports run\n\n```\npoetry run pytest tests/ --cov --cov-report html:htmlcov\n```\n\n### Custom Optimizers\n\nWhen you develop an optimizer based on the interface defined as part of\n`blackboxopt.base`, you can use `blackboxopt.testing` to directly test whether your\nimplementation follows the specification by adding a test like this to your test suite.\n\n```python\nfrom blackboxopt.testing import ALL_REFERENCE_TESTS\n\n@pytest.mark.parametrize("reference_test", ALL_REFERENCE_TESTS)\ndef test_all_reference_tests(reference_test):\n    reference_test(CustomOptimizer, custom_optimizer_init_kwargs)\n```\n\n## Building Documentation\n\nMake sure to install _all_ necessary dependencies:\n\n```\npoetry install --extras=all\n```\n\nThe documentation can be built from the repository root as follows:\n\n```\npoetry run mkdocs build --clean --no-directory-urls\n```\n\nFor serving it locally while working on the documentation run:\n\n```\npoetry run mkdocs serve\n```\n\n## Architectural Decision Records\n\n### Create evaluation result from specification\n\nIn the context of initializing an evaluation result from a specification, facing the\nconcern that having a constructor with a specification argument while the specification\nattributes end up as toplevel attributes and not summarized under a specification\nattribute we decided for unpacking the evaluation specification like a dictionary into\nthe result constructor to prevent the said cognitive dissonance, accepting that the\nunpacking operator can feel unintuitive and that users might tend to matching the\nattributes explictly to the init arguments.\n\n### Report multiple evaluations\n\nIn the context of many optimizers just sequentally reporting the individual evaluations\nwhen multiple evaluations are reported at once and thus not leveraging any batch\nreporting benefits, facing the concern that representing that common behaviour in the\noptimizer base class requires the definition of an abstract report single and an\nabstract report multi method for which the report single does not need to be implemented\nif the report multi is, we decided to refactor the arising redundancy into a function\n`call_functions_with_evaluations_and_collect_errors`, accepting that this increases the\ncognitive load when reading the code.\n\n## License\n\n`blackboxopt` is open-sourced under the Apache-2.0 license. See the [LICENSE](LICENSE)\nfile for details.\n\nFor a list of other open source components included in `blackboxopt`, see the file\n[3rd-party-licenses.txt](3rd-party-licenses.txt).\n',
    'author': 'Bosch Center for AI, Robert Bosch GmbH',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/boschresearch/blackboxopt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
