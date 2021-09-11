# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['apos']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'apos',
    'version': '0.2.1.2',
    'description': 'The backbone for message-driven applications.',
    'long_description': '# apos\n\nThe backbone for message-driven applications.\n\n## Summary\nThis Python library is designed to act as a software-level message broker, enabling a lightweight implementation of the publish-subscribe design pattern.\n\napos was born to accomplish two objectives:\n* Decouple the application layer from any interfaces\n* Develop reactive business functions\n\nWith apos, you can develop a message-driven application. This means that commands, events, and queries are sent to apos, which in return executes the functions that subscribe to these messages. This means that an adapter providing an external interface, may it be a web-API or a CLI, would not directly call application functions, but would rather send a message to apos, which will in return execute the business functions that subscribe to these messages. Equally, a business function would not call any other business function, but rather publishes an event, which other business functions can subscribe to and execute upon, controlled through apos.\n\n![](https://miro.medium.com/max/652/1*ZTxTLfH0FWRIQLAZFlBGEQ.png)\n\n## Context\nSee the Medium article linked below to read about why this library was created and how it is intended to be used. \nhttps://mkossatz.medium.com/a-backbone-for-message-driven-applications-ffdcef67824c\n\n\n## Installation\nThe library can be found on PyPi:\nhttps://pypi.org/project/apos/\n\n\n```shell\npip3 install apos\n```\n\n## Getting Started\n\nThe code below is a very lightweight example of how you can use apos for commands, queries, and events. \n\n```python\n\nfrom apos import apos\n\n\nclass RegisterUserCommand:\n    pass\n\n\nclass UserRegisteredEvent:\n    pass\n\n\nclass NewUserGreetedEvent:\n    pass\n\n\nclass RetrieveUserQuery:\n    pass\n\n\nclass RetrieveUserResponse:\n    pass\n\n\ndef register_user(command: RegisterUserCommand) -> None:\n    # Implementation of user registration\n    apos.publish_event(\n        UserRegisteredEvent())\n\n\ndef greet_new_user(event: UserRegisteredEvent) -> None:\n    # Implementation of user greeting\n    apos.publish_event(\n        NewUserGreetedEvent())\n\n\ndef retrieve_user(query: RetrieveUserQuery) -> RetrieveUserResponse:\n    # Implementation of user retrieval\n    return RetrieveUserResponse()\n\n\n# subscribing to messages (application configuration)\napos.subscribe_command(RegisterUserCommand, register_user)\napos.subscribe_event(UserRegisteredEvent, [greet_new_user])\napos.subscribe_query(RetrieveUserQuery, retrieve_user)\n\n# some interface adapter\napos.publish_command(RegisterUserCommand())\nevents = apos.get_published_events()\nprint(events)\nresponse: RetrieveUserResponse = apos.publish_query(RetrieveUserQuery())\nprint(response)\n\n\n```\n\n\n\n## Complete Examples\n\nYou can find examples in the examples directory of the projects repository.\nhttps://github.com/mkossatz/apos/tree/main/examples',
    'author': 'Max Kossatz',
    'author_email': 'max@kossatzonline.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mkossatz/apos',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
