from setuptools import setup
requires = [
    'beautifulsoup4>=4.9',
    'requests>=2.22',
]
long_desc = "![Logo](https://raw.githubusercontent.com/DAMcraft/gutefrage/main/gf-api-logo-new.png)\r\n\r\n[![PyPI](https://img.shields.io/pypi/v/gutefrage?color=g&logo=python&logoColor=white)](https://pypi.org/project/gutefrage/)\r\n[![PyPI - License](https://img.shields.io/pypi/l/gutefrage)]()\r\n[![Replit](https://img.shields.io/badge/replit.com-project-blue)](https://replit.com/@DAMcraft/Gutefrage-bot)\r\n### An unofficial [gutefrage.net](https://gutefrage.net) API made for Python.\r\n## Features\r\n* get question by name/url/id\r\n* get newest questions \r\n* like questions \r\n* reply to questions \r\n* TODO: post questions \r\n* TODO: reply replies\r\n## Get started\r\nAn short explenation of the basic features. You can find the full documentation [here](https://github.com/DAMcraft/gutefrage/wiki#documentation)\r\n### Installation\r\nGutefrage API can be installed like every other python package: `pip install gutefrage`\r\n### Basic usage\r\nIn this example we are going to mark a question from gutefrage.net as liked.\r\nFirst we have to create a new client with username and password:\r\n```python \r\nimport gutefrage as gf\r\n\r\ngfclient = gf.gutefrage(\"username\", \"password\")\r\n```\r\nTo interact with an specific question we need its **id**. To get the id we need its **stripped_title**. The stripped_title can be found in the last part of its url called like this:\r\n\r\nThe Url: `https://www.gutefrage.net/frage/wie-berechnet-man-die-quadratwurzel-aus-625`\r\n\r\nstripped_title: `wie-berechnet-man-die-quadratwurzel-aus-625`\r\n\r\nTo get the questions id we can use `.convert_to_id(string)`:\r\n```python \r\ntitle = \"wie-berechnet-man-die-quadratwurzel-aus-625\"\r\n\r\nid = gfclient.convert_to_id(title)\r\nprint(id)\r\n```\r\nWhat now is printed in the console is the question\'s id! For this question it\'s `57753709`.\r\nNow we have the id we can get the question by id:\r\n```python \r\nid = 57753709 \r\nquestion = gf.question(id)\r\n```\r\nNow we\'ve got the question, we can get lot of information about it:\r\n```python \r\ninformation = question.info()\r\n```\r\nAnd we can finally give it a like!\r\n```python \r\nquestion.like\r\n```\r\n## Documentation\r\nYou can find the full documentation [here](https://github.com/DAMcraft/gutefrage/wiki#documentation)\r\n"
setup(name='gutefrage',
      version='0.3.1',
      description='Unofficial GuteFrage api. Check https://github.com/DAMcraft/gutefrage/wiki on how to use it',
      url='https://github.com/DAMcraft/gutefrage',
      author='DAMcraft',
      author_email='',
      license='MIT',
      packages=['gutefrage'],
      zip_safe=False,
      install_requires=requires,
      long_description = long_desc,
      long_description_content_type = "text/markdown")