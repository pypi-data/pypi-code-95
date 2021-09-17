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
['ffmpeg-python>=0.2.0,<0.3.0',
 'imageio>=2.9.0,<3.0.0',
 'matplotlib>=3.4.2,<4.0.0',
 'numpy>=1.21.0,<2.0.0',
 'pandas>=1.3.0,<2.0.0',
 'pygame>=2.0.1,<3.0.0',
 'scipy>=1.7.1,<2.0.0',
 'tqdm>=4.61.2,<5.0.0']

setup_kwargs = {
    'name': 'westworld',
    'version': '0.1.2a1',
    'description': 'Multi-agent simulation library in Python',
    'long_description': '# Westworld\n![](docs/img/cover_hq_westworld1.jpg)\n\n## Description\n**Westworld** is a multi-agent simulation library, its goal to simulate and optimize systems and environments with multiple agents interacting. Its inspiration is drawn from Unity software and [Unity ML Agents](https://github.com/Unity-Technologies/ml-agents), adapted in Python. \n\nThe goal is to be able to simulate environments in logistics, retail, epidemiology, providing pre-coded spatial environments and communication between agents. Optimization can be included using heuristics as well as Reinforcement Learning.\n\n!!! warning "Experimental"\n    This library is extremely experimental, under active development and alpha-release\n    Don\'t expect the documentation to be up-to-date or all features to be tested\n    Please contact [us](mailto:theo.alves.da.costa@gmail.com) if you have any question\n\n*The name is of course inspired by the TV series Westworld, which is actually a gigantic multi-agent simulation system.*\n\n## Documentation\nDocumentation is available locally in docs folder or online at https://theolvs.github.io/westworld\n\n## Features\n### Current features\n- Easy creation of Grid and non-grid environments\n- Objects (Agents, Obstacles, Collectibles, Triggers)\n- Subclassing of different objects to create custom objects\n- Spawner to generate objects randomly in the environment\n- Basic rigid body system for all objects\n- Simple agent behaviors (pathfinding, wandering, random walk, fleeing, vision range)\n- Automatic maze generation\n- Layer integration to convert image to obstacle and snap it to a grid\n- Sample simulations and sample agents for classic simulations\n- Simulation visualization, replay and export (gif or video)\n\n### Roadmap features\n- More classic simulations and tutorials (boids, sugarscape)\n- Better pathfinding\n- Easy Reinforcement Learning integration with Stable Baselines\n- Other visualization functions than PyGame for web integration \n\n\n## Installation\n### Install from PyPi\nThe library is available on [PyPi](https://pypi.org/project/westworld/) via \n```\npip install westworld\n```\n\n### For developers\n- You can clone the github repo / fork and develop locally\n- Poetry is used for environment management, dependencies and publishing, after clone you can run \n\n```\n# To setup the environment\npoetry install\n\n# To run Jupyter notebook or a python console\npoetry run jupyter notebook\npoetry run python\n```\n\n## Contributors\n- [Théo Alves Da Costa](mailto:theo.alves.da.costa@gmail.com)\n\n## Javascript version\nA javascript version is being developed at https://github.com/TheoLvs/westworldjs\n\n',
    'author': 'Theo Alves Da Costa',
    'author_email': 'theo.alves.da.costa@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
