# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dagster_utils',
 'dagster_utils.config',
 'dagster_utils.contrib',
 'dagster_utils.contrib.data_repo',
 'dagster_utils.resources',
 'dagster_utils.resources.beam',
 'dagster_utils.resources.data_repo',
 'dagster_utils.testing',
 'dagster_utils.tests',
 'dagster_utils.tests.config',
 'dagster_utils.tests.contrib',
 'dagster_utils.tests.contrib.data_repo',
 'dagster_utils.tests.resources',
 'dagster_utils.tests.resources.data_repo',
 'dagster_utils.tests.support']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'argo-workflows>=5.0.0,<6.0.0',
 'dagster>=0.12.3,<0.13.0',
 'data-repo-client>=1.134.0,<2.0.0',
 'google-cloud-bigquery>=2.15.0,<3.0.0',
 'google-cloud-storage>=1.38.0,<2.0.0',
 'slackclient>=2.9.3,<3.0.0']

setup_kwargs = {
    'name': 'broad-dagster-utils',
    'version': '0.6.4',
    'description': 'Common utilities and objects for building Dagster pipelines',
    'long_description': '# Dagster Utils\n\nA collection of common utilities used by the Monster team to develop Dagster pipelines. Each subsection has its own readme explaining its contents.\n\n## How to use this library\n\nThis library is hosted on [PyPI](https://pypi.org/) and will work with most Python package managers out of the box. You can reference this package as `broad_dagster_utils`, e.g. for Poetry:\n\n```\n# pyproject.toml\n[tool.poetry.dependencies]\nbroad_dagster_utils = "^0.1.0"\n```\n\nNote that, despite this name, you\'ll need to import the package as `dagster_utils`, e.g.:\n```python\nfrom dagster_utils.typing import DagsterConfigDict\n```\n\n### Local Testing\nFor development against a local checkout in another project (i.e., a project with a dependency on `dagster_utils`), make the following adjustment to the project\'s `pyproject.toml`:\n```\nbroad-dagster-utils = {path = "<relative path to your dagster_utils checkout>", develop = true}\n```\n\n## Versioning\n\nThis library is versioned semantically.\n\n* **Major versions** (e.g. 1.4.6 -> 2.0.0) represent significant shifts in functionality and may alter the call signatures of core features of the library. You may need to follow a migration plan to upgrade to a new major version.\n* **Minor versions** (e.g. 1.4.6 -> 1.5.0) represent the removal or alteration of specific library features. They will not change core functionality, but the changelog should be reviewed before upgrading to avoid unexpected feature removals.\n* **Patch versions** (e.g. 1.4.6 -> 1.4.7) represent internal improvements or new features that do not alter existing functionality or call signatures. They may introduce deprecations, but they will never remove deprecated functions. You can always safely upgrade to a new patch version.\n* **Prerelease versions** (e.g. 1.4.6 -> 1.4.7-alpha.1) represent changes that have not yet been made part of an official release. See "Releasing a new version" below for more info.\n\n### Describing changes\n\nWhen describing changes made in a commit message, we want to be more thorough than usual, since bugs in dependencies are harder to diagnose. Break down the changes into these categories (omitting any categories that don\'t apply):\n\n* **New features** are changes that add functionality, such as new optional arguments for existing functions or entire new classes/functions. These changes should never require that existing code be changed.\n* **Bugfixes** are fairly self-explanatory - bugs that were identified and addressed. If fixing a bug required removing or altering existing features, make sure to list those under "breaking changes" as well.\n* **Deprecations** are features that are still usable, but have been marked as deprecated (and thus trigger a warning when used). They are planned to be removed in a future version. Always try to deprecate functionality before it\'s removed.\n* **Breaking changes** are changes that may break existing code using this library, such as renaming, removing, or reordering arguments to a function, deleting functionality (including deprecated functionality), or otherwise altering the library in ways that users will need to account for. Users should be able to use this section as a complete guide to upgrading their applications to be compatible with the new version.\n\n### Releasing a new version\n\nTo release a new version, determine what type of version increase your changes constitute (see the above guide) and update the version listed in `pyproject.toml` accordingly. Poetry has several [version bump commands](https://python-poetry.org/docs/cli/#version) to help with this. You can update the version in a dedicated PR or as part of another change. When a PR that updates the version number lands on master, an action will run to create a new tag for that version number, followed by cutting a Git release and publishing the new version to PyPI.\n',
    'author': 'Monster Dev',
    'author_email': 'monsterdev@broadinstitute.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/broadinstitute/dagster-utils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
