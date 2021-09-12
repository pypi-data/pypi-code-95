# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['powerplayer']
install_requires = \
['bs4>=0.0.1,<0.0.2',
 'click-help-colors>=0.9.1,<0.10.0',
 'click>=8.0.1,<9.0.0',
 'pafy>=0.5.5,<0.6.0',
 'playsound>=1.2.2,<2.0.0',
 'python-vlc>=3.0.12118,<4.0.0',
 'requests>=2.25.1,<3.0.0',
 'youtube_dl>=2021.6.6,<2022.0.0']

entry_points = \
{'console_scripts': ['pplay = powerplayer:main']}

setup_kwargs = {
    'name': 'powerplayer',
    'version': '0.1.7',
    'description': 'A command line interface to play music',
    'long_description': "# Powerplayer\nhttps://pypi.org/project/powerplayer/\nA python based terminal music player\nInspired by [Pauloo27](https://github.com/Pauloo27)'s [Tuner](https://github.com/Pauloo27/tuner)\n## OS\nTested in Windows 10(x64)\nShould work in MAC and Linux\n## Installation\n### Prerequisites\n\n- VLC Media Player\n- Python ^3.7\n### Windows\nOpen the powershell and type\n```pip install powerplayer```\n\n### Linux/Mac\nOpen the terminal and type\n```pip3 install powerplayer```\n\n## Usage\nAfter installation, type `pplay` in the terminal \nIt is fine if the output is this\n![image](https://user-images.githubusercontent.com/77975448/127959037-abe6f843-fafd-4f89-9c45-91d2bd6867b6.png)\n\n### Then to play music from youtube, type\n```pplay playfromyt songname```\n\nThe output should look like this\n\n![image](https://user-images.githubusercontent.com/77975448/125312335-cf050180-e351-11eb-9aae-2f5d20c1df9b.png)\n\n### To play music from file\n\nType\n```pplay playfrompc Filewithdirectory```\n\n\n\n",
    'author': 'Avanindra Chakraborty',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/AvanindraC/Powerplayer',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
