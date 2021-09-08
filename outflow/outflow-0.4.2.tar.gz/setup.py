# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['outflow',
 'outflow.core',
 'outflow.core.backends',
 'outflow.core.commands',
 'outflow.core.db',
 'outflow.core.db.alembic',
 'outflow.core.exceptions',
 'outflow.core.generic',
 'outflow.core.generic.context_manager',
 'outflow.core.logging',
 'outflow.core.pipeline',
 'outflow.core.tasks',
 'outflow.core.test',
 'outflow.core.test.test_cases',
 'outflow.core.workflow',
 'outflow.library',
 'outflow.library.tasks',
 'outflow.management',
 'outflow.management.commands',
 'outflow.management.models',
 'outflow.management.models.versions.default',
 'outflow.management.templates.pipeline_template',
 'outflow.ray',
 'outflow.ray.backends',
 'outflow.ray.tasks']

package_data = \
{'': ['*'],
 'outflow.management': ['templates/plugin_template/*',
                        'templates/plugin_template/plugin_namespace/*',
                        'templates/plugin_template/plugin_namespace/plugin_name/*',
                        'templates/plugin_template/plugin_namespace/plugin_name/models/*',
                        'templates/plugin_template/plugin_namespace/plugin_name/models/versions/*']}

install_requires = \
['alembic>=1.6,<1.7',
 'black>=21.8b0,<21.9.0',
 'declic>=1.0.2,<2.0.0',
 'jinja2>=2.11.3,<3.0.0',
 'networkx>=2.6,<2.7',
 'psycopg2-binary>=2.9.1,<2.10.0',
 'ray[default]>=1.6.0,<1.7.0',
 'simple-slurm>=0.1.7,<0.2.0',
 'sqlalchemy>=1.4,<1.5',
 'toml>=0.10.1,<0.11.0',
 'typeguard>=2.12.1,<2.13.0',
 'typing-extensions>=3.10.0.2,<3.11.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.8.1,<4.9.0'],
 'tests': ['pytest>=5.4.3,<6.0.0',
           'pytest-timeout>=1.4.2,<2.0.0',
           'pytest-cov>=2.12.1,<3.0.0',
           'pytest-postgresql>=2.6.1,<3.0.0']}

setup_kwargs = {
    'name': 'outflow',
    'version': '0.4.2',
    'description': 'Outflow is a framework that helps you create and execute sequential, parallel as well as distributed task workflows.',
    'long_description': '<div align="center">\n   <img src="https://gitlab.lam.fr/CONCERTO/outflow/-/raw/develop/docs/sections/images/logo.svg" width="500" style="max-width: 500px;">\n</div>\n\n<div align="center">\n\n<a href="https://pypi.org/project/outflow/">\n  <img src="https://img.shields.io/pypi/pyversions/outflow.svg" alt="python">\n</a>\n\n<a href="https://pypi.org/project/outflow/">\n  <img alt="PyPI" src="https://img.shields.io/pypi/v/outflow">\n</a>\n\n<a href="https://gitlab.com/outflow-project/outflow/-/pipelines/master/latest">\n  <img alt="pipeline status" src="https://gitlab.com/outflow-project/outflow/badges/master/pipeline.svg" />\n</a>\n\n<a href="https://gitlab.com/outflow-project/outflow/-/pipelines/master/latest">\n  <img alt="coverage report" src="https://gitlab.com/outflow-project/outflow/badges/master/coverage.svg" />\n</a>\n\n<a href=https://github.com/ambv/black>\n    <img src="https://img.shields.io/badge/code%20style-black-000000.svg">\n</a>\n\n<a href=\'https://docs.outflow.dev\'>\n  <img src=\'https://readthedocs.org/projects/outflow/badge/?version=latest\' alt=\'Documentation Status\' />\n</a>\n\n<a href="https://pypi.python.org/pypi/outflow">\n  <img src="https://img.shields.io/pypi/l/outflow.svg" alt="license" />\n</a>\n\n<a href="https://discord.outflow.dev/">\n  <img src="https://img.shields.io/badge/discord-support-7389D8?logo=discord&style=flat&logoColor=fff" alt="chat-discord-support" />\n</a>\n\n\n\n</div>\n\nOutflow is a framework that helps you build and run task workflows.\n\nThe api is as simple as possible while still giving the user full control over the definition and execution of the\nworkflows.\n\n**Feature highlight :**\n - Simple but powerful API\n - Support for **parallelized and distributed execution**\n - Centralized **command line interface** for your pipeline commands\n - Integrated **database** access, sqlalchemy models and alembic migrations\n - Executions and exceptions logging for **tracability**\n - Strict type and input/output checking for a **robust** pipeline\n\nCheck out our [documentation][outflow readthedocs] for more information.\n\n[outflow readthedocs]: https://docs.outflow.dev\n\n# Installing\n\nInstall and update using [pip](https://pip.pypa.io/en/stable/):\n\n```\npip install -U outflow\n```\n\n# Quick start\n\n## One file starter\n\nCreate a `pipeline.py` script:\n\n```python\n# -- pipeline.py\nfrom outflow.core.commands import Command, RootCommand\nfrom outflow.core.pipeline import Pipeline\nfrom outflow.core.tasks import Task\n\n\n# with the as_task decorator, the function will be automatically converted into a Task subclass\n# the signature of the function, including the return type, is used to determine task inputs and outputs\n@Task.as_task\ndef GetValues() -> {\'a\': str, \'b\': str}:\n    return {\'a\': \'hello\', \'b\': \'world\'}\n\n# default values can also be used as inputs\n@Task.as_task\ndef PrintValues(a: str, b: str, c: str = \'?\' ):\n    print(f"{a} {b}{c}")\n\n@RootCommand.subcommand()\nclass HelloWorld(Command):\n\n    def setup_tasks(self):\n        # instantiate tasks\n        get_values = GetValues()\n\n        # you can specify inputs value during instantiation\n        print_values = PrintValues(c="!")\n\n        # build the workflow\n        get_values >> print_values\n\n        # return the terminating task(s) of the workflow\n        # they will be used as entrypoints to navigate through the execution tree\n        return [print_values]\n\nif __name__ == "__main__":\n    # instantiate and run the pipeline\n    with Pipeline(\n        root_directory=None,\n        settings_module="outflow.core.pipeline.default_settings",\n        force_dry_run=True,\n    ) as pipeline:\n        result =  pipeline.run()\n\n```\n\nand run your first Outflow pipeline:\n\n```\n$ python pipeline.py hello_world\n```\n\n## A robust, configurable and well-organized pipeline\n\nYou had a brief overview of Outflow\'s features and you want to go further. Outflow offers command line tools to help you to start your pipeline project.\n\nFirst, we will need to auto-generate the pipeline structure -- a collection of files including the pipeline settings, the database and the cluster configuration, etc.\n\n```\n$ python -m outflow management create pipeline my_pipeline\n```\n\nThen, we have to create a plugin -- a dedicated folder regrouping the commands, the tasks as well as the description of the database (the models)\n```\n$ python -m outflow management create plugin my_namespace.my_plugin --plugin_dir my_pipeline/plugins/my_plugin\n```\n\nIn the my_pipeline/settings.py file, add your new plugin to the plugin list:\n\n```python\nPLUGINS = [\n    \'outflow.management\',\n    \'my_namespace.my_plugin\',\n]\n```\n\nand run the following command:\n\n```\n$ python ./my_pipeline/manage.py my_plugin\n```\n\nYou\'ll see the following output on the command line:\n\n```\n * outflow.core.pipeline.pipeline - pipeline.py:325 - INFO - No cluster config found in configuration file, running in a local cluster\n * my_namespace.my_plugin.commands - commands.py:49 - INFO - Hello from my_plugin\n```\n\nYour pipeline is up and running. You can now start adding new tasks and commands.\n\n# Contributing\n\nFor guidance on setting up a development environment and how to make a contribution to Outflow, see the [contributing guidelines](https://gitlab.lam.fr/CONCERTO/outflow/-/blob/master/CONTRIBUTING.md).\n',
    'author': 'Gregoire Duvauchelle',
    'author_email': 'gregoire.duvauchelle@lam.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://outflow.dev',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
