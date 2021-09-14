# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['god_like']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.0.1,<3.0.0', 'Werkzeug>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'god-like',
    'version': '1.0.1',
    'description': 'Flask for humans.',
    'long_description': '# GodLike\n\nNormally when I work on a web server I use express with JavaScript instead of flask with Python.\nEven though I like python, I don\'t like flask.\nExpress is a great tool for web development, it\'s in JavaScript though.\nSo I decided to write a version of express in Python.\n\nI came up with the name "god-like" because of how god like it would be to use express in Python.\n\nLets see how it works.\n\n```py\nfrom god_like import GodLike\n\napp = GodLike()\n\n@app.post("/")\ndef index(req, res):\n    res.send(f"The body is {req.body}")\n\napp.listen(port=8080)\n```\n\nFlask equivalent:\n\n```py\nfrom flask import Flask, request\n\napp = Flask(__name__)\n\n@app.route("/", methods["POST"])\ndef index():\n    return f"The body is {request.data.decode(\'utf-8\')}"\n\napp.run(port=8080)\n```\n\nDocumentation: https://hostedposted.github.io/god-like/latest/\n',
    'author': 'hostedposted',
    'author_email': 'hostedpostedsite@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hostedposted/god-like/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
