# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['_stories', '_stories.execute', 'stories']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'stories',
    'version': '5.0.0rc2',
    'description': 'Service objects designed with OOP in mind.',
    'long_description': '# Stories\n\n[![azure-devops-builds](https://img.shields.io/azure-devops/build/proofit404/stories/16?style=flat-square)](https://dev.azure.com/proofit404/stories/_build/latest?definitionId=16&branchName=master)\n[![azure-devops-coverage](https://img.shields.io/azure-devops/coverage/proofit404/stories/16?style=flat-square)](https://dev.azure.com/proofit404/stories/_build/latest?definitionId=16&branchName=master)\n[![pypi](https://img.shields.io/pypi/v/stories?style=flat-square)](https://pypi.org/project/stories)\n[![python](https://img.shields.io/pypi/pyversions/stories?style=flat-square)](https://pypi.org/project/stories)\n\nService objects designed with OOP in mind.\n\n**[Documentation](https://proofit404.github.io/stories) |\n[Source Code](https://github.com/proofit404/stories) |\n[Task Tracker](https://github.com/proofit404/stories/issues)**\n\nA paragraph of text explaining the goal of the library…\n\n## Pros\n\n- A feature\n- B feature\n- etc\n\n## Example\n\nA line of text explaining snippet below…\n\n```pycon\n\n>>> from dataclasses import dataclass\n>>> from typing import Callable\n>>> from stories import Story, I, State\n>>> from app.repositories import load_order, load_customer, create_payment\n\n>>> @dataclass\n... class Purchase(Story):\n...     I.find_order\n...     I.find_customer\n...     I.check_balance\n...     I.persist_payment\n...\n...     def find_order(self, state):\n...         state.order = self.load_order(state.order_id)\n...\n...     def find_customer(self, state):\n...         state.customer = self.load_customer(state.customer_id)\n...\n...     def check_balance(self, state):\n...         if not state.order.affordable_for(state.customer):\n...             raise Exception\n...\n...     def persist_payment(self, state):\n...         state.payment = self.create_payment(\n...             order_id=state.order_id, customer_id=state.customer_id\n...         )\n...\n...     load_order: Callable\n...     load_customer: Callable\n...     create_payment: Callable\n\n>>> purchase = Purchase(\n...     load_order=load_order,\n...     load_customer=load_customer,\n...     create_payment=create_payment,\n... )\n\n>>> state = State(order_id=1, customer_id=1)\n\n>>> purchase(state)\n\n>>> state  # doctest: +SKIP\n\n>>> state.payment.was_received()\nFalse\n\n```\n\n## Questions\n\nIf you have any questions, feel free to create an issue in our\n[Task Tracker](https://github.com/proofit404/stories/issues). We have the\n[question label](https://github.com/proofit404/stories/issues?q=is%3Aopen+is%3Aissue+label%3Aquestion)\nexactly for this purpose.\n\n## Enterprise support\n\nIf you have an issue with any version of the library, you can apply for a paid\nenterprise support contract. This will guarantee you that no breaking changes\nwill happen to you. No matter how old version you\'re using at the moment. All\nnecessary features and bug fixes will be backported in a way that serves your\nneeds.\n\nPlease contact [proofit404@gmail.com](mailto:proofit404@gmail.com) if you\'re\ninterested in it.\n\n## License\n\n`stories` library is offered under the two clause BSD license.\n\n<p align="center">&mdash; ⭐ &mdash;</p>\n<p align="center"><i>The <code>stories</code> library is part of the SOLID python family.</i></p>\n',
    'author': 'Artem Malyshev',
    'author_email': 'proofit404@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/stories',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<3.10',
}


setup(**setup_kwargs)
