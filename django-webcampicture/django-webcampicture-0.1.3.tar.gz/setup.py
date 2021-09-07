# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['webcampicture', 'webcampicture.migrations']

package_data = \
{'': ['*'],
 'webcampicture': ['static/webcampicture/css/*',
                   'static/webcampicture/js/*',
                   'templates/webcampicture/*']}

setup_kwargs = {
    'name': 'django-webcampicture',
    'version': '0.1.3',
    'description': 'A Django app to provide a WebcamPictureField, derived from ImageField.',
    'long_description': '# django-webcampicture\n\n**django-webcampicture** is a very simple Django app that provides a specialization of Django\'s native `ImageField`: `WebcamPictureField`, which allows users to save images taken from their webcams, instead of uploading.\n\n## Quick start\n\n1. Install using `pip`:\n\n```bash\npip install django-webcampicture\n```\n\n2. Add *"webcampicture"* to your **INSTALLED_APPS** setting like this:\n\n```python\nINSTALLED_APPS = [\n    ...\n    \'webcampicture\',\n]\n```    \n\n3. Use the field in your models:\n\n```python\nfrom django.db import models\nfrom webcampicture.fields import WebcamPictureField\n\nclass Child(models.Model):\n    name = models.CharField("Name", max_length=255)\n\n    # WebcamPictureField takes the same parameters as ImageField\n    picture = WebcamPictureField("Picture", upload_to="pictures", blank=True)\n\n    # Image URL example...\n    @property\n    def picture_url(self):\n        if self.picture and hasattr(self.picture, "url"):\n            return self.picture.url\n\n```\n\n4. Remember to include in your templates:\n\n```html\n{% load static %}\n<link rel="stylesheet" href="{% static "webcampicture/css/webcampicture.css" %}">\n<script src="{% static \'webcampicture/js/webcampicture.js\' %}"></script>\n```\n\n## Demo\n\n![demo](demo.gif)\n\n## Settings and default values\n\n```python\nWEBCAM_BASE64_PREFIX = "data:image/png;base64,"\nWEBCAM_CONTENT_TYPE = "image/png"\nWEBCAM_FILENAME_SUFFIX = ".png"\n```\n\n## Overridable templates\n\n```text\nwebcampicture/webcampicture.html\n```\n',
    'author': 'rnetonet',
    'author_email': 'rneto@rneto.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rnetonet/django-webcampicture',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
