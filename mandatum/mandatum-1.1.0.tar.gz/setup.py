# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mandatum']

package_data = \
{'': ['*']}

install_requires = \
['rich>=7.0.0,<8.0.0']

setup_kwargs = {
    'name': 'mandatum',
    'version': '1.1.0',
    'description': 'A python framework to make beatiful cli applications',
    'long_description': '# Mandatum\nMandatum is a python framework based on rich-python to create beatiful Command-Line-Interface applications in no time. It can create interface for your application in an object oriented approach\n\n## Installation\nTo install via pip type the following command\n```bash\npip install mandatum\n```\n\nOR\n\nInstall poetry\n```bash\npip install poetry\n```\n\nClone this repo\n```bash\ngit clone https://github.com/CalculusAI/mandatum\n```\n\nChange directory to mandatum and type\n```bash\npoetry install\n```\n\n## Getting Started\nLets create a basic application with mandatum\n\n```python\nimport mandatum\n\n# Initial setup\nmenu = mandatum.Menu(options=["Opt1", "Opt2"], bold_text=True)\nprompt = mandatum.Prompt(color="blue")\nalert = mandatum.Alert(bold_text=True)\nwarning = mandatum.Warning()\n\nif __name__ == "__main__":\n\n    # Displaying Menu\n    menu.start()\n\n    # User name\n    name = prompt.input("\\nEnter your name : ")\n    print(name)\n\n    # Alerts\n    alert.alert("\\nAlerting")\n\n    # Warning\n    warning.warn(message="\\nWarning!", bold_text=True)\n```\n\n## License\nmandatum is licensed under the terms of MIT license',
    'author': 'Zayed Malick',
    'author_email': 'zayedmalick13@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CalculusAI/mandatum',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
