# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ninja_auth']

package_data = \
{'': ['*']}

install_requires = \
['django-ninja>=0.13.2,<0.14.0']

setup_kwargs = {
    'name': 'django-ninja-auth',
    'version': '0.1.4',
    'description': 'Django authorization views adapted to django-ninja',
    'long_description': '# Django Ninja Auth: Use Django authorization infrastructure with Django Ninja\n\nDjango Ninja Auth is a minimalistic python package that leverages the funcionalities of `django.contrib.auth` to backend-only [Django](https://www.djangoproject.com/) projects that use the exceptional [Django Ninja](https://django-ninja.rest-framework.com/).\n\n## Install\n1. `pip install django-ninja-auth`.\n2. Add the router to your `NinjaAPI`. Assuming you created a project according to [Django Ninja\'s tutorial](https://django-ninja.rest-framework.com/tutorial/) just follow this template in `api.py`:\n```python\nfrom ninja import NinjaAPI\nfrom ninja_auth.api import router as auth_router\n\napi = NinjaAPI()\napi.add_router(\'/auth/\', auth_router)\n```\n3. Build the front-end infrastructure to interact with `your-api.com/api/auth/` 🚀.\n\n## Documentation\nIf you followed the steps above, everything should be documented in your OpenAPI/Swagger UI under `your-api.com/api/docs`. No unnecessary documentation here 😎.\n\n## CSRF\nUnfortunately, Django Ninja will [force you to use CSRF protection](https://django-ninja.rest-framework.com/tutorial/csrf/). It is your responsibility to build a front-end that takes care of this, adding it in the API\'s schema does not make sense.\n\nIf you ask me, I\'d just use `SESSION_COOKIE_SAMESITE = \'strict\'` and `SESSION_COOKIE_HTTPONLY = True` (default) and forget about CSRF attacks. "But there are old browsers that... 😭😭"   - If your cookies get stolen because you use Internet Explorer it\'s not my fault.\n\n## Password Reset Email\nWhen you call `/api/auth/request_password_reset/` you only need to provide an email address. If the address corresponds to an actual user, Django will send an email to that address with a token to reset the password of the user (of course, you need to configure email sending in your `settings.py`). By default, the email is built using a [horrendous template](https://github.com/django/django/blob/main/django/contrib/admin/templates/registration/password_reset_email.html) provided by the `django.contrib.admin` app. If you are not using such app, Django will complain because the template does not exist. My recommendation is to build your own beautiful template and place it in `registration/password_reset_email.html` under some of your *templates directories*. To build that template you can use the following variables:\n- `protocol`: usually `http` or `https`.\n- `domain`: whatever was before `/api/auth/request_password_reset/` when the request was made.\n- `uid`: the user\'s id in base64.\n- `user`: an object containing data of the user. You can retrieve the username via `{{ user.get_username }}`.\n- `site_name`: your site\'s name.\n- `token`: the reset token\n',
    'author': 'Martín Ugarte',
    'author_email': 'contact@martinugarte.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mugartec/django-ninja-auth',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
