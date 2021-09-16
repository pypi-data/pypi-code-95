# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['admin_edit_lock']

package_data = \
{'': ['*'], 'admin_edit_lock': ['static/admin_edit_lock/*']}

install_requires = \
['Django>=2.2']

setup_kwargs = {
    'name': 'django-admin-edit-lock',
    'version': '0.3.1',
    'description': 'django-admin-edit-lock is a Django application used in admin to prevent simultaneous edit by more than one users.',
    'long_description': '# django-admin-edit-lock\n\n> :warning: Correct operation relies on cache. Therefore, the current version will be unreliable in cases where the default local-memory cache backend is used, along with multiple application server worker (see https://github.com/demestav/django-admin-edit-lock/issues/1).\n\n## Setup\nInstall package using `pip`:\n\n```shell\npython -m pip install django-admin-edit-lock\n```\n\nAdd it to the installed apps:\n```python\nINSTALLED_APPS = [\n    ...\n    "admin_edit_lock",\n    ...\n]\n```\n\n## Configuration\nThere are two one mandatory settings:\n\n### `ADMIN_EDIT_LOCK_DURATION` \nDefines how long each edit lock should last. The value is in seconds. For example:\n\n```python\nADMIN_EDIT_LOCK_DURATION = 60\n```\n\nwill keep the lock for sixty seconds.\n\nThe lock is being updated regularly (every 5 seconds) as long as the user is still editing the object. Therefore this value needs to be larger than 5 seconds. This configuration will probably be removed in the future, as it does not really offer any value by being user-configurable. The only case this affects the user is how long the lock will remain after the user finished editing. For example, the user updated the lock at 10:00:00 (i.e. the lock expires at 10:01:00) and the user exits the edit screen (closer tab or saves or navigates back etc.) at 10:00:10. For the remaining 50 seconds, the lock will be there without any real purpose.\n\n### `ADMIN_EDIT_LOCK_MAX_DURATION`\nDefines for how long a user can keep the same lock. The value is in seconds.\n\nThis prevents a user to keep the maintain the edit rights of an object indefinitely. This is useful in cases where a user unintentionally keeps the edit screen open and therefore not allowing other users to edit the object.\n\n## Usage\nUse the `AdminEditLockMixin` to enable edit lock on a model. \n\nFor example:\n\n```python\n# models.py\nfrom django.db import models\n\nclass Book(models.Model):\n    name = models.CharField(max_length=100)\n```\n\n```python\n# admin.py\nfrom django.contrib import admin\nfrom admin_edit_lock.admin import AdminEditLockMixin\n\n\nclass BookAdmin(AdminEditLockMixin, admin.ModelAdmin):\n    class Meta:\n        model = Book\n```\n\n## Roadmap\n- Customize messages\n- ~~Extending the lock expiry time through AJAX call~~\n- ~~Optionally set a limit to how much the lock can be extended~~\n\n## Acknowledgements\nThis project is inspired by https://github.com/jonasundderwolf/django-admin-locking . This project differentiates by utilizing the Django permissions to decide whether a user can edit or not. Further, this project uses the messages middleware to notify the users of the lock status.\n',
    'author': 'Demetris Stavrou',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/demestav/django-admin-edit-lock',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
