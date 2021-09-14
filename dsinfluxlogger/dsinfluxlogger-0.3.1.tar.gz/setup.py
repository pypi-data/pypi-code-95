# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dsinfluxlogger']

package_data = \
{'': ['*']}

install_requires = \
['aioinflux>=0.9,<0.10',
 'datastreamservicelib>=1.10,<2.0',
 'flatten-dict>=0.3,<0.4']

entry_points = \
{'console_scripts': ['dsinfluxlogger = '
                     'dsinfluxlogger.console:influxlogger_cli']}

setup_kwargs = {
    'name': 'dsinfluxlogger',
    'version': '0.3.1',
    'description': 'Log datamessages to influxdb',
    'long_description': '==============\ndsinfluxlogger\n==============\n\nLog PubSubDataMessages (see datastreamcorelib) to InfluxDB, this is a pretty quick and dirty implementation\nand definitely not optimal.\n\nFor optimal write performance we should add a plugin system that allows\none to convert the payload from the PubSubDataMessages into line-protocol decorated\ncustom classes https://aioinflux.readthedocs.io/en/stable/usage.html#writing-user-defined-class-objects\n\nThe quick-and-dirty optimization is to batch writes into pandas dataframes, which has the not\ninsignificant drawback of adding pandas/numpy to our requirements.\n\nDocker\n------\n\nFor more controlled deployments and to get rid of "works on my computer" -syndrome, we always\nmake sure our software works under docker.\n\nIt\'s also a quick way to get started with a standard development environment.\n\nSSH agent forwarding\n^^^^^^^^^^^^^^^^^^^^\n\nWe need buildkit_::\n\n    export DOCKER_BUILDKIT=1\n\n.. _buildkit: https://docs.docker.com/develop/develop-images/build_enhancements/\n\nAnd also the exact way for forwarding agent to running instance is different on OSX::\n\n    export DOCKER_SSHAGENT="-v /run/host-services/ssh-auth.sock:/run/host-services/ssh-auth.sock -e SSH_AUTH_SOCK=/run/host-services/ssh-auth.sock"\n\nand Linux::\n\n    export DOCKER_SSHAGENT="-v $SSH_AUTH_SOCK:$SSH_AUTH_SOCK -e SSH_AUTH_SOCK"\n\nCreating a development container\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n\nBuild image, create container and start it::\n\n    docker build --ssh default --target devel_shell -t dsinfluxlogger:devel_shell .\n    docker create --name dsinfluxlogger_devel -p 58770:58770 -v `pwd`":/app" -it -v /tmp:/tmp `echo $DOCKER_SSHAGENT` dsinfluxlogger:devel_shell\n    docker start -i dsinfluxlogger_devel\n\npre-commit considerations\n^^^^^^^^^^^^^^^^^^^^^^^^^\n\nIf working in Docker instead of native env you need to run the pre-commit checks in docker too::\n\n    docker exec -i dsinfluxlogger_devel /bin/bash -c "pre-commit install"\n    docker exec -i dsinfluxlogger_devel /bin/bash -c "pre-commit run --all-files"\n\nYou need to have the container running, see above. Or alternatively use the docker run syntax but using\nthe running container is faster::\n\n    docker run -it --rm -v `pwd`":/app" dsinfluxlogger:devel_shell -c "pre-commit run --all-files"\n\nTest suite\n^^^^^^^^^^\n\nYou can use the devel shell to run py.test when doing development, for CI use\nthe "tox" target in the Dockerfile::\n\n    docker build --ssh default --target tox -t dsinfluxlogger:tox .\n    docker run -it --rm -v `pwd`":/app" `echo $DOCKER_SSHAGENT` dsinfluxlogger:tox\n\nProduction docker\n^^^^^^^^^^^^^^^^^\n\nThere\'s a "production" target as well for running the application (change "myconfig.toml" for config file)::\n\n    docker build --ssh default --target production -t dsinfluxlogger:latest .\n    docker run -it --name dsinfluxlogger -v myconfig.toml:/app/config.toml -p 58770:58770 -it -v /tmp:/tmp `echo $DOCKER_SSHAGENT` dsinfluxlogger:latest\n\n\nLocal Development\n-----------------\n\nTLDR:\n\n- Create and activate a Python 3.8 virtualenv (assuming virtualenvwrapper)::\n\n    mkvirtualenv -p `which python3.8` my_virtualenv\n\n- change to a branch::\n\n    git checkout -b my_branch\n\n- install Poetry: https://python-poetry.org/docs/#installation\n- Install project deps and pre-commit hooks::\n\n    poetry install\n    pre-commit install\n    pre-commit run --all-files\n\n- Ready to go, try the following::\n\n    dsinfluxlogger --defaultconfig >config.toml\n    dsinfluxlogger -vv config.toml\n\nRemember to activate your virtualenv whenever working on the repo, this is needed\nbecause pylint and mypy pre-commit hooks use the "system" python for now (because reasons).\n\nRunning "pre-commit run --all-files" and "py.test -v" regularly during development and\nespecially before committing will save you some headache.\n',
    'author': 'Eero af Heurlin',
    'author_email': 'eero.afheurlin@iki.fi',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/advian-oss/python-dsinfluxlogger/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
