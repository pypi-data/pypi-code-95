# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['westworld',
 'westworld._deprecated',
 'westworld.agents',
 'westworld.algorithms',
 'westworld.algorithms.pathfinding',
 'westworld.assets',
 'westworld.assets.sprites',
 'westworld.environment',
 'westworld.objects',
 'westworld.optimization',
 'westworld.simulation',
 'westworld.utils']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.2,<4.0.0',
 'numpy>=1.21.0,<2.0.0',
 'pandas>=1.3.0,<2.0.0',
 'tqdm>=4.61.2,<5.0.0']

setup_kwargs = {
    'name': 'westworld',
    'version': '0.1.0',
    'description': 'Multi-agent simulation library in Python',
    'long_description': '# Westworld\n![](docs/docs/img/cover_hq_westworld1.jpg)\n\n# Description\n**Westworld** is a multi-agent simulation library, its goal to simulate and optimize systems and environments with multiple agents interacting. Its inspiration is drawn from Unity software and [Unity ML Agents](https://github.com/Unity-Technologies/ml-agents), adapted in Python. \n\nThe goal is to be able to simulate environments in logistics, retails, epidemiology, providing pre-coded spatial environments and communication between agents. Optimization can be included using heuristics as well as Reinforcement Learning.\n\n*Library under active development*\n\n*The name is of course inspired by the TV series Westworld, which is actually a gigantic multi-agent simulation system.*\n\n# Documentation\nDocumentation is available locally in docs folder or online at https://theolvs.github.io/westworld\n\n\n# Repo structure\n\n```\n- docs : documentation of the library\n- examples : simulation examples and development tests\n- westworld : library\n```',
    'author': 'Theo Alves Da Costa',
    'author_email': 'theo.alves.da.costa@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
