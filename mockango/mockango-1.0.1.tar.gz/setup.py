# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mockango',
 'mockango.management',
 'mockango.management.commands',
 'mockango.utils']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mockango',
    'version': '1.0.1',
    'description': 'django-admin fixture generator command',
    'long_description': '# mockango\ndjango-admin commands which generate fixture data for your given apps\'s models using Mimesis data generator\n## requirements\n```shell\npip install django\npip install mimesis\npip install pyyaml\npip install colorama\n```\n## installation\n```shell\npip intall mockango\n```\n```python\nINSTALLED_APPS = [\n  ...\n  \'mockango\',\n]\n```\n## usage\n```app_labels```(positional):  labels of app you need fixture data for them\n\n```--num```(optional)(default=10): number of object generate for each model\n\n```--foramt```(optional)(default=yaml): format of fixture file\n\n```--locale```(optional)(default=en): supported mimesis locales\n\n```shell\npython manage.py generatedata posts --num 5 --format yaml --locale fa\n```\n## examples\nmodels.py\n```python\nclass Post(models.Model):\n  title = models.Charfield(max_length=200)\n  text = models.TextField()\n  is_publish = models.BooleanField(default=False)\n  published_date = models.DateTimeField()\n  CATEGORIES = [\n    (\'T\', \'Tutorail\'),\n    (\'N\', \'Normal\'),\n    ]\n  category = models.CharField(max_length=1, choices=CATEGORIES)\n```\nsettings.py\n```python\nINSTALLED_APPS = [\n  ...\n  \'mockango\',\n  \'posts\',\n]\n```\n```shell\npython manage.py generatedata posts --num 5\n```\nposts/fixture/post/fixture_file.yaml\n```yaml\n- fields:\n    category: T\n    is_publish: false\n    published_date: 2018-02-21 05:29:26.253161\n    text: Messages can be sent to and received from ports, but these messages must\n      obey the so-called "port protocol." It is also a garbage-collected runtime system.\n      Atoms can contain any character if they are enclosed within single quotes and\n      an escape convention exists which allows any character to be used within an\n      atom. The syntax {D1,D2,...,Dn} denotes a tuple whose arguments are D1, D2,\n      ... Dn. Do you come here often?\n    title: Messages can be sent to and received from ports, but these messages must\n      obey the so-called "port protocol."\n  model: posts.post\n  pk: 1\n- fields:\n    category: N\n    is_publish: false\n    published_date: 2009-01-25 08:37:08.793574\n    text: She spent her earliest years reading classic literature, and writing poetry.\n      Do you have any idea why this is not working? Any element of a tuple can be\n      accessed in constant time. Its main implementation is the Glasgow Haskell Compiler.\n      Tuples are containers for a fixed number of Erlang data types.\n    title: They are written as strings of consecutive alphanumeric characters, the\n      first character being lowercase.\n  model: posts.post\n  pk: 2\n- fields:\n    category: T\n    is_publish: false\n    published_date: 2013-01-03 11:28:01.825650\n    text: He looked inquisitively at his keyboard and wrote another sentence. Any\n      element of a tuple can be accessed in constant time. Haskell is a standardized,\n      general-purpose purely functional programming language, with non-strict semantics\n      and strong static typing. Atoms are used within a program to denote distinguished\n      values. Atoms can contain any character if they are enclosed within single quotes\n      and an escape convention exists which allows any character to be used within\n      an atom.\n    title: They are written as strings of consecutive alphanumeric characters, the\n      first character being lowercase.\n  model: posts.post\n  pk: 3\n- fields:\n    category: T\n    is_publish: false\n    published_date: 2006-06-24 11:19:25.527136\n    text: Haskell features a type system with type inference and lazy evaluation.\n      It is also a garbage-collected runtime system. Messages can be sent to and received\n      from ports, but these messages must obey the so-called "port protocol." The\n      sequential subset of Erlang supports eager evaluation, single assignment, and\n      dynamic typing. Tuples are containers for a fixed number of Erlang data types.\n    title: The syntax {D1,D2,...,Dn} denotes a tuple whose arguments are D1, D2, ...\n      Dn.\n  model: posts.post\n  pk: 4\n- fields:\n    category: T\n    is_publish: true\n    published_date: 2006-10-17 12:10:48.115520\n    text: Tuples are containers for a fixed number of Erlang data types. It is also\n      a garbage-collected runtime system. He looked inquisitively at his keyboard\n      and wrote another sentence. The Galactic Empire is nearing completion of the\n      Death Star, a space station with the power to destroy entire planets. Messages\n      can be sent to and received from ports, but these messages must obey the so-called\n      "port protocol."\n    title: Ports are created with the built-in function open_port.\n  model: posts.post\n  pk: 5\n```\n## If You Find It Useful\nHi my friend if you find mockango useful please give it one star or share with your friends.\nI think it can be imporve it so if you find something missing make issue\n**Thanks**\n',
    'author': 'iliark1382',
    'author_email': 'iliark82@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/iliark1382/mockango',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
