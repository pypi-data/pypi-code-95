# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['flask_aserto']

package_data = \
{'': ['*']}

install_requires = \
['aserto>=0.1.3,<0.2.0', 'typing-extensions>=3.10.0,<4.0.0']

setup_kwargs = {
    'name': 'flask-aserto',
    'version': '0.1.2',
    'description': 'Aserto integration for Flask',
    'long_description': '# Aserto Flask middleware\nThis is the official library for integrating [Aserto](https://www.aserto.com/) authorization into your [Flask](https://github.com/pallets/flask) applications.\n\nFor a example of what this looks like in a running Flask app and guidance on connecting an identity provider, see the [PeopleFinder app example](https://github.com/aserto-dev/aserto-python/tree/main/packages/flask-aserto/peoplefinder_example).\n\n## Features\n### Add authorization checks to your routes\n```py\nfrom flask_aserto import AsertoMiddleware, AuthorizationError\n\n\napp = Flask(__name__)\naserto = AsertoMiddleware(**aserto_options)\n\n\n@app.route("/api/users/<id>", methods=["GET"])\n@aserto.authorize\ndef api_user(id: str) -> Response:\n    # Raises an AuthorizationError if the `GET.api.users.__id`\n    # policy returns a decision of "allowed = false" \n    ...\n```\n### Automatically create a route to serve a [Display State Map](https://docs.aserto.com/authorizer-guide/display-state-map)\n```py\n# Defaults to creating a route at the path "/__displaystatemap" \naserto.register_display_state_map(app)\n```\n### Perform more finely controlled authorization checks\n```py\n@app.route("/api/users/<id>", methods=["GET"])\nasync def api_user(id: str) -> Response:\n    # This also automatically knows to check the `GET.api.users.__id` policy\n    if not await aserto.check("allowed"):\n        raise AuthorizationError()\n\n    ...\n```\n',
    'author': 'Aserto, Inc.',
    'author_email': 'pypi@aserto.com',
    'maintainer': 'authereal',
    'maintainer_email': 'authereal@aserto.com',
    'url': 'https://github.com/aserto-dev/aserto-python/tree/HEAD/packages/flask-aserto',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
