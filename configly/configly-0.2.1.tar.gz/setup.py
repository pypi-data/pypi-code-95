# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['configly', 'configly.interpolators']

package_data = \
{'': ['*']}

extras_require = \
{'toml': ['toml'], 'vault': ['hvac'], 'yaml': ['ruamel.yaml']}

setup_kwargs = {
    'name': 'configly',
    'version': '0.2.1',
    'description': '',
    'long_description': '![CircleCI](https://img.shields.io/circleci/build/gh/schireson/configly/master) [![codecov](https://codecov.io/gh/schireson/configly/branch/master/graph/badge.svg)](https://codecov.io/gh/schireson/configly) [![Documentation Status](https://readthedocs.org/projects/configly/badge/?version=latest)](https://configly.readthedocs.io/en/latest/?badge=latest)\n\n## TL;DR\n\n```yaml\n# config.yml\nfoo:\n    bar: <% ENV[REQUIRED] %>\n    baz: <% ENV[OPTIONAL, true] %>\nlist_of_stuff:\n    - fun<% ENV[NICE, dament] %>al\n    - fun<% ENV[AGH, er] %>al\n```\n\n```python\n# app.py\nconfig = Config.from_yaml(\'config.yml\')\n\nprint(config.foo.bar)\nprint(config.foo[\'baz\'])\nfor item in config.list_of_stuff:\n    print(item)\n```\n\n```bash\npip install configly[yaml]\n```\n\n## Introduction\n\nLoading configuration is done in every (application) project, and yet it is often\noverlooked and condidered too easy or straightforward to bother using a library\nto manage doing it.\n\nTherefore, we often see code like this:\n\n```python\n# config.py\nimport os\n\n# Maybe it\'s following 12factor and loading all the config from the environment.\nconfig = {\n    \'log_level\': os.getenv(\'LOG_LEVEL\'),\n    \'database\': {\n        # At least here, I can nest values if I want to organize things.\n        \'password\': os.environ[\'DATABASE_PASSWORD\'],\n        \'port\': int(os.environ[\'DATABASE_PORT\']),\n    }\n}\n```\n\nor this\n\n```python\n# config.py\nimport os\n\nclass Config:\n    log_level = os.getenv(\'LOG_LEVEL\')\n\n    # Here it\'s not so easy to namespace\n    database_password = os.environ[\'DATABASE_PASSWORD\']\n    database_port = int(os.environ[\'DATABASE_PORT\'])\n\n\n# Oh goodness!\nclass DevConfig(Config):\n    environment = \'dev\'\n```\n\nor this\n\n```python\nimport configparser\n# ...🤢... Okay I dont even want to get into this one.\n```\n\nAnd this is all assuming that everyone is loading configuration at the outermost entrypoint!\nThe two worst possible outcomes in configuration are:\n\n* You are loading configuration lazily and/or deeply within your application, such that it\n  hits a critical failure after having seemingly successfully started up.\n* There is not a singular location at which you can go to see all configuration your app might\n  possibly be reading from.\n\n\n## The pitch\n\n`Configly` asserts configuration should:\n* Be centralized\n  * One should be able to look at one file to see all (env vars, files, etc) which must exist for the\n    application to function.\n* Be comprehensive\n  * One should not find configuration being loaded secretly elsewhere\n* Be declarative/static\n  * code-execution (e.g. the class above) in the definition of the config inevitably makes it\n    hard to interpret, as the config becomes more complex.\n* Be namespacable\n  * One should not have to prepend `foo_` namespaces to all `foo` related config names\n* Be loaded, once, at app startup\n  * (At least the _definition_ of the configuration you\'re loading)\n* (Ideally) have structured output\n  * If something is an `int`, ideally it would be read as an int.\n\nTo that end, the `configly.Config` class exposes a series of classmethods from which your config\ncan be loaded. It\'s largely unimportant what the input format is, but we started with formats\nthat deserialize into at least `str`, `float`, `int`, `bool` and `None` types.\n\n```python\n# Currently supported input formats.\nconfig = Config.from_yaml(\'config.yml\')\nconfig = Config.from_json(\'config.json\')\nconfig = Config.from_toml(\'config.toml\')\n```\n\nGiven an input `config.yml` file:\n\n```yaml\n# config.yml\nfoo:\n    bar: <% ENV[REQUIRED] %>\n    baz: <% ENV[OPTIONAL, true] %>\nlist_of_stuff:\n    - fun<% ENV[NICE, dament] %>al\n    - fun<% ENV[AGH, er] %>al\n```\n\nA couple of things jump out:\n* Most importantly, whatever the configuration value is, it\'s intreted as a literal value in the\n  format of the file which loads it. I.E. loading `"true"` from the evironment in a yaml file\n  will yield a python `True`. Ditto `"1"`, or `"null"`.\n* Each `<% ... %>` section indicates a variable\n* `ENV` is an "interpolator" which knows how to obtain environment variables\n* `[VAR]` Will raise an error if that piece of config is not found\n* `[VAR, true]` Will `VAR` to the value after the comma\n* The interpolation can be a sub-portion of a key (`fun<% ENV[NICE, dament] %>al` interpolates\n  to "fundamental"). Another example being `\'<% ENV[X, 3] %>\'` interpolates to `\'1\'` instead of `1`\n\n\nNow that you\'ve loaded the above configuration:\n\n```python\n# app.py\nconfig = Config.from_yaml(\'config.yml\')\n\n# You can access namespaced config using dot access\nprint(config.foo.bar)\n\n# You have use index syntax for dynamic, or non-attribute-safe key values.\nprint(config.foo[\'baz\'])\n\n# You can iterate over lists\nfor item in config.list_of_stuff:\n    print(item)\n\n# You can *generally* treat key-value maps as dicts\nfor key, value in config.foo.items():\n    print(key, value)\n\n# You can *actually* turn key-value maps into dicts\ndict(config.foo) == config.foo.to_dict()\n```\n\n## Installing\n\n```bash\n# Basic installation\npip install configly\n\n# To use the yaml config loader\npip install configly[yaml]\n\n# To use the toml config loader\npip install configly[toml]\n\n# To use the vault config loader\npip install configly[vault]\n```\n',
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/schireson/configly',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4',
}


setup(**setup_kwargs)
