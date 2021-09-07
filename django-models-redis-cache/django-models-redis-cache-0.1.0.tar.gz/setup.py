# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_models_redis_cache', 'django_models_redis_cache.tests']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.0,<4.0', 'redis>=3.5.3,<4.0.0']

setup_kwargs = {
    'name': 'django-models-redis-cache',
    'version': '0.1.0',
    'description': 'Django Models Redis Cache (DMoReCa), library that gives your specified Django models regular caching via Redis',
    'long_description': '# django-models-redis-cache\n\n## **Django Models Redis Cache (DMoReCa), library that gives your specified Django models regular caching via Redis**\n\nFor one project, I needed to work with redis, but redis-py provides a minimum level of work with redis. I didn\'t find any Django-like ORM for redis, so I wrote library [python-redis-orm](https://github.com/gh0st-work/python_redis_orm/) ([PyPI](https://pypi.org/project/python-redis-orm/)).\n\nAlso, if you are searching for just django-like redis ORM, please check [django-redis-orm](https://github.com/gh0st-work/django_redis_orm/) ([PyPI](https://pypi.org/project/django-redis-orm/)).\n\n**And this library is port to Django that provides easy-to-use Django models caching via Redis**.\n\n### Working with this library, you are expected:\n\n- Fully works in 2021\n- Easy adaptation to your needs\n- Adequate informational messages and error messages\n- Built-in RedisRoot class that stores specified models, with:\n    - **redis_instance** setting - your redis connection (from redis-py)\n    - **prefix** setting - prefix of this RedisRoot to be stored in redis\n    - **ignore_deserialization_errors** setting - do not raise errors, while deserealizing data\n    - **save_consistency** setting - show structure-first data\n    - **economy** setting - to not return full data and save some requests (usually, speeds up your app on 80%)\n- CRUD (Create Read Update Delete), in our variation: save, get, filter, order, update, delete:\n    - `example_instance = ExampleModel(example_field=\'example_data\').save()` - to create an instance and get its data dict\n    - `filtered_example_instances = redis_root.get(ExampleModel, example_field=\'example_data\')` - to get all ExampleModel instances with example_field filter and get its data dict\n    - `ordered_instances = redis_root.order(filtered_example_instances, \'-id\')` - to get ordered filtered_example_instances by id (\'-\' for reverse)\n    - `updated_example_instances = redis_root.update(ExampleModel, ordered_instances, example_field=\'another_example_data\')` - to update all ordered_instances example_field with value \'another_example_data\' and get its data dict\n    - `redis_root.delete(ExampleModel, updated_example_instances)` - to delete updated_example_instances\n\n\n# Installation\n`pip install django-models-redis-cache`\n\n[Here is PyPI](https://pypi.org/project/django-models-redis-cache/)\n\nAdd "django_models_redis_cache" to your INSTALLED_APPS setting like this::\n\n    INSTALLED_APPS = [\n        ...\n        \'django_models_redis_cache\',\n    ]\n\n# Usage\n\n### You can set this part in your project settings.py\n\n```python\nfrom django_models_redis_cache.core import *\n\n\ndef get_connection_pool():\n    host = \'localhost\'\n    port = 6379\n    db = 0\n    connection_pool = redis.ConnectionPool(\n        decode_responses=True,\n        host=host,\n        port=port,\n        db=db,\n    )\n    return connection_pool\n\n\nREDIS_ROOTS = {\n    \'test_caching_root\': RedisRoot(\n        prefix=\'test_caching\',\n        connection_pool=get_connection_pool(),\n        ignore_deserialization_errors=True,\n        economy=True\n    )\n}\n\n```\n\n### Run in the background\n\nYou can just copy it to:\n\n`app/management/commands/command_name.py`\n    \nAnd just run with:\n\n`python manage.py command_name`\n    \nHelp:\n\n[Django custom management commands](https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/)\n    \n[How to import something from settings](https://stackoverflow.com/a/14617309)\n\n```python\n\nif redis_roots:\n    if type(redis_roots) == dict:\n        some_caching_redis_root = redis_roots[\'test_caching_root\']\n        some_caching_redis_root.register_django_models({\n            DjangoModelToCache1: {\n                \'enabled\': True,\n                \'ttl\': 60 * 5,  # Cache every 5 mins\n                \'prefix\': f\'test_caching_root-DjangoModelToCache1-cache\', # please make it unique\n            },\n            # DjangoModelToCache2: {\n            #     \'enabled\': True,\n            #     \'ttl\': 60 * 10,  # Cache every 10 mins\n            #     \'prefix\': f\'test_caching_root-DjangoModelToCache2-cache\', # please make it unique\n            # },\n            # ...\n        })\n        # another_caching_redis_root = redis_roots[\'another_test_caching_root\']\n        # some_caching_redis_root.registered_django_models({...})\n        roots_to_cache = [\n            some_caching_redis_root,\n            # another_caching_redis_root\n        ]\n        print(\'STARTING CACHING\')\n        while True:\n            for redis_root in roots_to_cache:\n                redis_root.check_cache()\n    else:\n        raise Exception(\'redis_roots must be dict\')\nelse:\n    raise Exception(\'No redis_roots\')\n\n```\n\n',
    'author': 'Anton Nechaev',
    'author_email': 'antonnechaev990@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gh0st-work/django_models_redis_cache',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
