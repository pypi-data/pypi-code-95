# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetryupvers']

package_data = \
{'': ['*']}

install_requires = \
['docopt>=0.6.2,<0.7.0',
 'gitlab-ps-utils>=0.1.4,<0.2.0',
 'semver>=2.13.0,<3.0.0',
 'tomlkit>=0.7.2,<0.8.0']

entry_points = \
{'console_scripts': ['ppuv = poetryupvers.main:run']}

setup_kwargs = {
    'name': 'poetryupvers',
    'version': '0.2.0',
    'description': 'Semantic versioning on a pyproject.toml',
    'long_description': '# Automatic Semantic Versioning for Poetry\n\nHandle automatically incrementing the version in your pyproject.toml\n\n## Installation\n\n```\npip install ppuv\n```\n\n## Upversion process\n\nThis package executes the following processes:\n- open pyproject.toml and read version\n- parse version into a semver-friendly format\n- read the commit history of the repo from HEAD to the latest numeric tag\n- searches for keyword matches in the commit messages compared to the content of the messages.json file\n- if any keywords match with phrases defined the major, minor, or patch json objects, then the bump type will reflect major, minor, or patch\n    - For example, if a commit message with "[BREAKING CHANGE]" is found in the history, the bump type will be major\n- bump version based on version type determined\n- update pyproject.toml file\n\n## Usage\n\n```\nUsage:\n    ppuv bump [--messages-file=<path>]\n    ppuv push-bump [--config-user=<user>] [--config-email=<email>] [--remote=<remote>] [--branch=<branch>]\n    ppuv generate-release-notes [--save] [--path=<path>]\n\nOptions:\n    -h, --help      Show Usage.\n\nCommands:\n    bump                    Bump the version of the pyproject.toml file. \n                            This is based on specific keywords, defined in the messages.json file, \n                            found in commit messages ranging from HEAD to the last numeric tag\n    \n    push-bump               Commits the pyproject.toml file to the git repository.\n                            Contains multiple options to run this command in a CI pipeline\n\n    generate-release-notes  Generates release notes based on commits and related MRs in GitLab\n\nArguments:\n    messages-file   Override the messages file JSON (text snippets denoting the version bump), \n                    if not using a local messages.json or installed messages.json\n    save            Writes release notes to file (default path = ./release_notes.md)\n    path            Override release notes file path\n    config-user     Sets git user\n    config-email    Sets git user email\n    remote          Sets git remote name (ex: origin)\n    branch          Sets git push branch\n```\n\n### Bump version with default configuration\n\n```bash\nppuv bump\n```\n\n### Bump version with overriden messages.json\n\n```bash\n# If you have a messages.json defined directly at the root of your repository\nppuv bump\n\n# If you have a different location for your messages.json (or a different filename)\nppuv bump --messages-file=<path-to-file>\n```\n\n### Example messages.json\n\n```json\n{\n    "major": "[BREAKING CHANGE]",\n    "minor": [\n        "[New Feature]",\n        "Add",\n        "Update"\n    ],\n    "patch": [\n        "[BUGFIX]",\n        "Fix"\n    ]\n}\n```\n\n## Generate release notes (For GitLab only)\n\n```bash\nppuv generate-release-notes\n```\n\nThis process is dependent on the following environment variables being set:\n- CI_PROJECT_ID: The ID of the project, should be available within a CI pipeline. \n    You will need to set this manually if you run this command outside of a GitLab CI pipeline\n- CI_SERVER_URL: The base url of the GitLab instance itself (e.g https://gitlab.com). \n    Also should be available within a CI pipeline, but you will need to set it manually to run this script outside of a GitLab CI pipeline\n- ACCESS_TOKEN: Personal access token or Project-level access token. \n    Used to interact with the GitLab API to retrieve the related MRs to the git commits. You will need to store this as a CI/CD variable\n\nThe process is the following:\n\n- Grab a list of commit hashes between HEAD and the latest numeric tag\n- Iterate over the hashes and send a request to \n    [`projects/{id}/repository/commits/{commit}/merge_requests`](https://docs.gitlab.com/ee/api/commits.html#list-merge-requests-associated-with-a-commit)\n    to retrieve any related MRs to that commit\n- Append the MR title and ID to an internal dictionary to prevent any duplicate entries\n- Format each MR title and ID to a markdown bullet\n- Print out release notes and write them to a file',
    'author': 'Michael Leopard',
    'author_email': 'mleopard@gitlab.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/gitlab-org/professional-services-automation/tools/utilities/poetryupvers',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
