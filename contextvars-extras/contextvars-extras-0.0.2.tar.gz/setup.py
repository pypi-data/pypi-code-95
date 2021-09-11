# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['contextvars_extras', 'contextvars_extras.integrations']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'contextvars-extras',
    'version': '0.0.2',
    'description': 'Contextvars made easy (WARNING: unstable alpha version. Things may break).',
    'long_description': 'contextvars-extras\n==================\n\n|tests badge| |docs badge|\n\n**Warning!**\n\n**The code is at the early development stage, and may be unstable. Use with caution.**\n\n``contextvars-extras`` is a set of extensions for the Python\'s `contextvars`_ module.\n\nIn case you are not familiar with the `contextvars`_ module, its `ContextVar`_ objects\nwork like Thread-Local storage, but better: they are both thread-safe and async task-safe,\nand they can be copied (all existing vars copied in O(1) time), and then you can run\na function in the copied and isolated context.\n\n.. _contextvars: https://docs.python.org/3/library/contextvars.html\n.. _ContextVar: https://docs.python.org/3/library/contextvars.html#contextvars.ContextVar\n\nThe `contextvars`_ is a powerful module, but its API seems too low-level.\n\nSo this ``contextvars_extras`` package provides some higher-level additions on top of the\nstandard API, like, for example, organizing `ContextVar`_ objects into registry classes,\nwith nice ``@property``-like access:\n\n.. code:: python\n\n    from contextvars_extras.registry import ContextVarsRegistry\n\n    class CurrentVars(ContextVarsRegistry):\n        locale: str = \'en\'\n        timezone: str = \'UTC\'\n\n    current = CurrentVars()\n\n    # calls ContextVar.get() under the hood\n    current.timezone  # => \'UTC\'\n\n    # calls ContextVar.set() under the hood\n    current.timezone = \'GMT\'\n\n    # ContextVar() objects can be reached as lass members\n    CurrentVars.timezone.get()  # => \'GMT\'\n\nThat makes your code more readable (no more noisy ``.get()`` calls),\nand it is naturally firendly to `typing`_, so static code analysis features\n(like type checkers and auto-completion in your IDE) work nicely.\n\n.. _typing: https://docs.python.org/3/library/typing.html\n  \nIt also allows things like injecting context variables as arguments to functions:\n\n.. code:: python\n\n    @current.as_args\n    def do_something_useful(locale: str, timezone: str):\n        print(f"locale={locale!r}, timezone={timezone!r}")\n\n    do_something_useful()  # prints: locale=\'UTC\', timezone=\'en\'\n\nand overriding the values:\n\n.. code:: python\n   \n    with current(locale=\'en_GB\', timezone=\'GMT\'):\n        do_something_useful()  # prints: locale=\'en_GB\', timezone=\'GMT\'\n\nThere are some more features, check out the full documentation...\n\n- Read the Docs: https://contextvars-extras.readthedocs.io/en/latest/\n\n\n.. |tests badge| image:: https://github.com/vdmit11/contextvars-extras/actions/workflows/tests.yml/badge.svg\n  :target: https://github.com/vdmit11/contextvars-extras/actions/workflows/tests.yml\n  :alt: Tests Status\n\n.. |docs badge| image:: https://readthedocs.org/projects/contextvars-extras/badge/?version=latest\n  :target: https://contextvars-extras.readthedocs.io/en/latest/?badge=latest\n  :alt: Documentation Status\n',
    'author': 'Dmitry Vasilyanov',
    'author_email': 'vdmit11@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vdmit11/contextvars-extras',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
