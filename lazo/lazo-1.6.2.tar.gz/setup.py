# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['lazo', 'lazo.commands']

package_data = \
{'': ['*'], 'lazo': ['templates/*']}

install_requires = \
['click>=6,<7', 'colorama', 'pygments', 'requests', 'websocket-client']

entry_points = \
{'console_scripts': ['lazo = lazo.__cli__:cli']}

setup_kwargs = {
    'name': 'lazo',
    'version': '1.6.2',
    'description': 'lazo',
    'long_description': "## Lazo\n\n[![PyPI version](https://badge.fury.io/py/lazo.svg)](https://badge.fury.io/py/lazo)\n\nSmall utility to work with Rancher. It has been developd to be used in CI environments.\n\nCurrent features:\n\n - get infos on running cluster/project/workload\n - get docker image info\n - upgrade workload \n - execute commands in running containers\n \n  \n### Install\n\n    $ pip install lazo\n    \nor using [pipx](https://pypi.org/project/pipx/) \n\n    $ pipx install lazo\n    \n### Help        \n        \n    $ lazo --help\n    Usage: lazo [OPTIONS] COMMAND [ARGS]...\n    \n    Options:\n      --version        Show the version and exit.\n      --env\n      -v, --verbosity  verbosity level\n      -q, --quit       no output\n      -d, --dry-run    dry-run mode\n      --debug          debug mode\n      -h, --help       Show this message and exit.\n    \n    Commands:\n      docker\n      rancher    \n\n\n### Environment varialbles      \n\n- RANCHER_BASE_URL as `--base-url`\n- RANCHER_KEY as `--key`\n- RANCHER_SECRET as `--secret`\n- RANCHER_CLUSTER as `--cluster`\n- RANCHER_PROJECT as `--project`\n- RANCHER_INSECURE as `--inxecure`\n- DOCKER_REPOSITORY as `--repository`\n\nYou can inspect your default configuration with:\n\n    $ lazo --defaults\n    Env                  Value                                              Origin\n    repository           https://hub.docker.com/v2\n    auth\n    base_url\n    cluster\n    insecure             False\n    project\n    use_names            False\n    \nor list handler environment variables with:\n\n    $ lazo --env\n    Env                  Value\n    DOCKER_REPOSITORY    -- not set --\n    RANCHER_AUTH         -- not set --\n    RANCHER_BASE_URL     -- not set --\n    RANCHER_CLUSTER      -- not set --\n    RANCHER_INSECURE     -- not set --\n    RANCHER_PROJECT      -- not set --\n    RANCHER_USE_NAMES    -- not set --      \n\n\n### Examples\n\n#### Rancher\n\n##### get infos on running workload\n      \n    $ lazo rancher -i -n info -p cluster1:bitcaster -w bitcaster:bitcaster\n    Workload infos:\n    Image: bitcaster/bitcaster:0.3.0a15\n    Command: ['stack']\n    imagePullPolicy: Always    \n\n##### upgrading workload\n\n    $ export RANCHER_KEY=key\n    $ export RANCHER_SECRET=secret\n    $ lazo upgrade saxix/devpi:latest \\\n           --base-url https://rancher.example.com/v3/\n           --cluster c-wwk6v\n           --project p-xd4dg\n \n##### use stdin to read credentials\n\n    $  cat .pass.txt | lazo --stdin \\\n        upgrade bitcaster:bitcaster \\\n        bitcaster/bitcaster:0.3.0a10 \\\n        --insecure\n\n##### execute command in running container\n\n    $ lazo shell bitcaster:db -- ls -al /var/log\n    total 432\n    drwxr-xr-x 1 root        root       4096 Jan  1 01:39 .\n    drwxr-xr-x 1 root        root       4096 Dec 26 00:00 ..\n    drwxr-xr-x 1 root        root       4096 Jan  1 01:39 apt\n    -rw-r--r-- 1 root        root      74886 Jan  1 01:39 dpkg.log\n    -rw-r--r-- 1 root        root      32000 Jan  1 01:39 faillog\n    drwxr-xr-x 2 root        root       4096 May 25  2017 sysstat\n\n\n#### Docker\n\n##### list image available tags\n\n    $ lazo docker info saxix/devpi\n    latest\n    2.3\n    2.2\n    2.1\n    2.0\n    1.1\n\n##### get information on image\n\n    $ lazo docker info library/python --filter '3\\.6.*alpine3.8' --size\n    3.6-alpine3.8                  26.2MiB\n    3.6.8-alpine3.8                26.2MiB\n    3.6.7-alpine3.8                26.2MiB\n    3.6.6-alpine3.8                26.2MiB\n",
    'author': 'sax',
    'author_email': 's.apostolico@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/saxix/lazo',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
