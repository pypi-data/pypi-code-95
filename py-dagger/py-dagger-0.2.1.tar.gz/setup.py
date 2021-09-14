# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dagger',
 'dagger.dag',
 'dagger.data_structures',
 'dagger.dsl',
 'dagger.input',
 'dagger.output',
 'dagger.runtime.argo',
 'dagger.runtime.cli',
 'dagger.runtime.local',
 'dagger.serializer',
 'dagger.task']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'py-dagger',
    'version': '0.2.1',
    'description': 'Define sophisticated data pipelines with Python and run them on different distributed systems (such as Argo Workflows).',
    'long_description': "# Dagger\n\nDefine sophisticated data pipelines and run them on different distributed systems (such as Argo Workflows).\n\n![Python Versions Supported](https://img.shields.io/badge/python-3.8+-blue.svg)\n[![Latest PyPI version](https://badge.fury.io/py/py-dagger.svg)](https://badge.fury.io/py/py-dagger)\n[![Test Coverage (Codecov)](https://codecov.io/gh/larribas/dagger/branch/main/graph/badge.svg?token=fKU68xYUm8)](https://codecov.io/gh/larribas/dagger)\n![Continuous Integration](https://github.com/larribas/dagger/actions/workflows/continuous-integration.yaml/badge.svg)\n\n---\n\n## Features\n\n- Define tasks and DAGs, and compose them together seamlessly.\n- Create dynamic for loops and map-reduce operations.\n- Run your DAGs locally or using a distributed workflow orchestrator (such as Argo Workflows).\n- Take advantage of advanced runtime features (e.g. Retry strategies, Kubernetes scheduling directives, etc.)\n- ... All with a simple _Pythonic_ DSL that feels just like coding regular Python functions.\n\n\nOther nice features of _Dagger_ are: Zero dependencies, 100% test coverage, great documentation and plenty of examples to get you started.\n\n\n## Installation\n\n_Dagger_ is published to the Python Package Index (PyPI) under the name `py-dagger`. To install it, you can simply run:\n\n```\npip install py-dagger\n```\n\n## Looking for Tutorials and Examples?\n\nCheck our [Documentation Portal](https://larribas.me/dagger)!\n\n\n\n\n## Architecture Overview\n\n_Dagger_ is built around 3 components:\n\n- A set of __core data structures__ that represent the intended behavior of a DAG.\n- A __domain-specific language (DSL)__ that uses metaprogramming to capture how a DAG should behave, and represents it using the core data structures.\n- Multiple __runtimes__ that inspect the core data structures to run the corresponding DAG, or prepare the DAG to run in a specific pipeline executor.\n\n\n[![components](docs/assets/images/diagrams/components.png)](docs/assets/images/diagrams/components.png)\n\n\n## How to contribute\n\nDo you have some feedback about the library? Have you implemented a Serializer or a Runtime that may be useful for the community? Do you think a tutorial or example could be improved?\n\nEvery contribution to _Dagger_ is greatly appreciated.\n\nPlease read our [Contribution Guidelines](CONTRIBUTING.md) for more details.\n\n\n\n### Local development\n\nWe use Poetry to manage the dependencies of this library. In the codebase, you will find a `Makefile` with some useful commands to run and test your contributions. Namely:\n\n- `make install` - Install the project's dependencies\n- `make test` - Run tests and report test coverage. It will fail if coverage is too low.\n- `make ci` - Run all the quality checks we run for each commit/PR. This includes type hint checking, linting, formatting and documentation.\n- `make build` - Build the project.\n- `make docker-build` - Package the project in a Docker image\n- `make docs-build` - Build the documentation portal.\n- `make docs-serve` - Serve the documentation portal.\n- `make k3d-set-up` - Create a k3d cluster and image registry for the project.\n- `make k3d-docker-push` - Build and push the project's Docker image to the local k3d registry.\n- `make k3d-install-argo` - Install Argo on k3d, for local testing of Argo Workflows.\n- `make k3d-tear-down` - Destroy the k3d cluster and registry.\n",
    'author': 'larribas',
    'author_email': 'lorenzo.s.arribas@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/larribas/dagger',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
