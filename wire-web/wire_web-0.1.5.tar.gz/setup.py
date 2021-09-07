# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wire_web', 'wire_web.groups', 'wire_web.utils']

package_data = \
{'': ['*']}

install_requires = \
['multidict>=5.1.0,<6.0.0']

setup_kwargs = {
    'name': 'wire-web',
    'version': '0.1.5',
    'description': 'Wire the web',
    'long_description': '<h1 align="center">Wire</h1>\n<p align="center"> Easy, fast, stable </p>\n\nWire is designed to provide the user with the greatest possible comfort when creating Rest APIs or entire websites.\nEverything is simple and, above all, intuitively designed. No focus on superfluous configurations. Everything works, simply.\n\n🔑 Key features\n- intuitive, due to the clear design\n- simple, due to the fast learning curve\n- practical, through the great editor support\n- minimalistic, no superfluous functions\n\n#### What is Wire and what is not\nWire is not a HighSpeed framework. Wire is probably not ready for production. Wire is a spare time project of mine. Wire is self-contained. It doesn\'t need anything, except for an ASGI server. So it\'s like Starlette. \nI would appreciate if you use Wire, try it and give me your feedback.\n \n#### Participate in Wire\nYou are welcome to collaborate on Wire. However, you should maintain the codestyle, and also follow PEP 8 (the Python style guide). \n\n#### Wire disadvantages\nWire is still deep in development, which is why some features are still missing. So are still missing:\n- Setting headers\n- Reading and setting cookies\n\n#### Examples\nHere is the most basic example of wire\n```py\nfrom wire_web import Wire, Request\n\napp = Wire()\n\n@app.get("/home")\nasync def home(req: Request):\n\treturn "Welcome home"\n```\n\nYou want to build a RestAPI? No problem\n\n```py\nfrom wire_web import Wire, Request\n\n\napp = Wire()\n\n\n@app.get("/api")\ndef api(req: Request):\n\treturn {"name": "Leo", "age": 16}\n```\n\nYou want to send HTML files? Wire got your back\n\n```py\nfrom wire_web import Wire, Request\nfrom wire_web.responses import HTMLResponse\n\n\napp = Wire()\n\n@app.get("/html")\nasync def home(req: Request):\n\twith open("home.html", "r") as f:\n\t\tdata = f.read()\n\treturn HTMLResponse(data)\n```\n\n**Changes incoming**\n\nJoin our [discord](https://discord.gg/EtqGfBVuZS) !\n',
    'author': 'Leo B.',
    'author_email': 'bernerdoodle@outlook.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://wire.bernerdev.de/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
