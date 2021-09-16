# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mad_gui',
 'mad_gui.components',
 'mad_gui.components.dialogs',
 'mad_gui.components.dialogs.plugin_selection',
 'mad_gui.config',
 'mad_gui.models',
 'mad_gui.models.local',
 'mad_gui.plot_tools.labels',
 'mad_gui.plot_tools.plots',
 'mad_gui.plugins',
 'mad_gui.qt_designer',
 'mad_gui.utils',
 'mad_gui.windows']

package_data = \
{'': ['*'], 'mad_gui.qt_designer': ['images/*']}

install_requires = \
['PySide2==5.15.1',
 'pandas',
 'pyqtgraph==0.11.0',
 'typing-extensions>=3.10.0,<4.0.0']

entry_points = \
{'console_scripts': ['mad-gui = mad_gui:start_gui']}

setup_kwargs = {
    'name': 'mad-gui',
    'version': '0.2.0a3',
    'description': 'GUI for annotating and processing IMU data.',
    'long_description': '# MaD GUI \n**M**achine Learning \n**a**nd \n**D**ata Analytics \n**G**raphical \n**U**ser \n**I**nterface\n\n[![Test and Lint](https://github.com/mad-lab-fau/mad-gui/workflows/Test%20and%20Lint/badge.svg)](https://github.com/mad-lab-fau/mad-gui/actions/workflows/test_and_lint.yml)\n[![Documentation Status](https://readthedocs.org/projects/mad-gui/badge/?version=latest)](https://mad-gui.readthedocs.io/en/latest/?badge=latest)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n## Contents of this readme\n- [What is it?](#what-is-it)\n- [How do I use it (videos)](#how-do-i-use-it-videos)\n- [How do I get the GUI to work on my machine?](#how-do-i-get-the-gui-to-work-on-my-machine)\n- [How can I test the GUI using your example data on my computer?](#how-can-i-test-the-gui-using-your-example-data-on-my-computer)\n- [Can I use it with data of my specific system or a specific algorithm?](#can-i-use-it-with-data-of-my-specific-system-or-a-specific-algorithm)\n- [Can I change something at the core of the GUI?](#can-i-change-something-at-the-core-of-the-gui)\n\n\n##  What is it?\nThe MaD GUI is a framework for processing time series data.\nIts use-cases include visualization, annotation (manual or automated), and algorithmic processing of visualized data and annotations.\n\n## How do I use it?\n### Videos\nBy clicking on the images below, you will be redirected to YouTube. In case you want to follow along on your own machine, check out the section [How do I get the GUI to work on my machine?](#how-do-i-get-the-gui-to-work-on-my-machine) first.\n\n[<img src="./docs/_static/images/video_thumbnails/loading_and_navigating.png" width="200px">](https://www.youtube.com/watch?v=akxcuFOesC8 "MaD GUI - Loading data and navigating in the plot")\n[<img src="./docs/_static/images/video_thumbnails/annotations.png" width="200px">](https://www.youtube.com/watch?v=VWQKYRRRGVA "MaD GUI - Labelling data manually or using an algorithm")\n[<img src="./docs/_static/images/video_thumbnails/sync.png" width="200px">](https://www.youtube.com/watch?v=-GI5agFOPRM "MaD GUI - Synchronize video and sensor data")\n\n### Shortcuts\nPlease watch the videos linked above, if you want to learn more about the different actions.\n\n| Shortcut                     | Mode      |Action |\n|------------------------------|-----------|-------|\n| `a`, `e`, `r`, `s`, `Esc`    | all       | Switch between modes *Add label*, *Edit label*, *Remove label*, *Synchronize data*|\n| `Space`                      | Add label | Can be used instead of `Left Mouse Click` |\n| `1`, `2`, `3`,... `TAB`      | Add label | Navigate in the pop-up window |\n| `Shift` + `Left Mouse Click` | Add label | Start a new label directly when setting the end of a label |\n| `Ctrl` + `Left Mouse Click`  | Add label | Add a single event |\n\n## How do I get the GUI to work on my machine?\nBelow, we present two options how to obtain and run the GUI.\nHowever, this will only enable you to look at our example data.\nYou want to load data of a specific format/system or want to use a specific algorithm? \nIn this case please refer to [Can I use it with data of my specific system or a specific algorithm?](#can-i-use-it-with-data-of-my-specific-system-or-a-specific-algorithm)\n\n## How can I test the GUI using your example data on my computer?\n\nFirst, you need to download the example data.\nRight click on [this link](https://github.com/mad-lab-fau/mad-gui/raw/main/example_data/sensor_data.csv), select `Save link as...` and save it - you have to change the file ending from \\*.txt to \\*.csv before saving.\nIf you also want to check out synchronization with a video file, click on [this link](https://github.com/mad-lab-fau/mad-gui/releases/download/v0.2.0-alpha.1/video.mp4) and save it on your machine. Next, use one of the following two options (for testing it on Windows, we recommend Option A).\n\n### Option A: Standalone executable\n\n| Operating system       | What to do                                        |\n|------------------------|---------------------------------------------------|\n| Windows                | Download our exemplary executable [here](https://github.com/mad-lab-fau/mad-gui/releases/download/v0.2.0-alpha.1/mad_gui.exe). <br /> Note: If prompted with a dialog `Windows protected your PC`, click `More info` and then select `Run anyway` |\n| other                  | [Contact us](mailto:malte.ollenschlaeger@fau.de)  \n\nStart the program and then you can open the previously downloaded example data as shown in [How do I use it (videos)?](#how-do-i-use-it-videos)\n\n### Option B: Using the python package\n```\npip install mad_gui\n```\nMake sure to include the underscore.\nIf you do not include it, you will install a different package.\n\nThen, from your command line either simply start the GUI (first line) or pass additional arguments (second line):\n```\nmad-gui\npython -m mad_gui.start_gui --data_dir C:/my_data\n```\n\nAlternatively, within a python script use our [start_gui](https://github.com/mad-lab-fau/mad-gui/blob/main/mad_gui/start_gui.py#L26) \nfunction and hand it over the path where your data resides, `<data_path>` like `C:/data` or `/home/data/`: \n```\nfrom mad_gui import start_gui\nstart_gui(<data_path>)\n```\n\nNow you can open the previously downloaded example data as shown in [How do I use it (videos)?](#how-do-i-use-it-videos)\n\n## Can I use it with data of my specific system or a specific algorithm?\nYes, however it will need someone who is familiar with python to perform the steps described in [Customization](https://mad-gui.readthedocs.io/en/latest/customization.html).\nYou do not have experience with python but still want to load data from a specific system? [Contact us!](mailto:malte.ollenschlaeger@fau.de)\n\nDevelopers can get basic information about the project setup in our [Developer Guidelines](https://mad-gui.readthedocs.io/en/latest/developer_guidelines.html).\nIf you want to extend the GUI with your custom plugins, e.g. for loading data of a specific system,\nor adding an algorithm, the necessary information can be found in our documentation regarding [Customization](https://mad-gui.readthedocs.io/en/latest/customization.html).\n\n## Can I change something at the core of the GUI?\nSure, for more information, please take a look at our [Contribution Guidelines](https://mad-gui.readthedocs.io/en/latest/contribution_guidelines.html#contribution-guidelines).\n',
    'author': 'Malte Ollenschlaeger',
    'author_email': 'malte.ollenschlaeger@fau.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mad-lab-fau/mad-gui',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
