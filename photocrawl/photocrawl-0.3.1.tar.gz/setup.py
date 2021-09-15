# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['photocrawl']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.3.2,<9.0.0',
 'loguru>=0.4.1,<0.5.0',
 'matplotlib>=3.2.1,<4.0.0',
 'pandas>=1.0.3,<2.0.0',
 'pendulum>=2.1.2,<3.0.0',
 'pyexifinfo>=0.4.0,<0.5.0',
 'seaborn>=0.10.1,<0.11.0',
 'typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['photocrawl = photocrawl.__main__:app']}

setup_kwargs = {
    'name': 'photocrawl',
    'version': '0.3.1',
    'description': 'Analysis script of photography habits.',
    'long_description': '# PhotoCrawl: A Photography Analyzer\n\nA simple script to run analysis and get insight on my use of equipment and settings in my practice of photography.\n\n## Install\n\n### Prerequisites\n\nThis script runs on Python3.6.1+, and requires the following libraries: [`PyExifInfo`][pyexifinfo], `matplotlib`, `seaborn`, `pandas`, `pendulum`, `typer` and `loguru`.\nMost importantly, it also requires that you have the amazing [ExifTool][exiftool] package by Phil Harvey.\n\n### Install\n\nThis code is compatible with `Python 3.6+`.\nIf for some reason you have a need for it, you can simply install it in your virtual enrivonment with:\n```bash\npip install photocrawl\n```\n\n## Usage\n\nWith this package installed in the activated enrivonment, it can be called through `python -m photocrawl` or through a newly created `photocrawl` command.\n\n\nDetailed usage goes as follows:\n```bash\nUsage: photocrawl [OPTIONS] [IMAGES]\n\n  Crawl and ensemble of pictures to run analysis of their metadata and get\n  insight on one\'s use of equipment and settings in their practice of\n  photography.\n\nArguments:\n  [IMAGES]  Location, relative or absolute, of the images directory you wish\n            to crawl.\n\n\nOptions:\n  --output-dir TEXT               Location, either relative or absolute, of\n                                  the output directory.  [default: outputs]\n\n  --show-figures / --no-show-figures\n                                  Whether or not to show figures when plotting\n                                  insights.  [default: False]\n\n  --save-figures / --no-save-figures\n                                  Whether or not to save figures when plotting\n                                  insights.  [default: False]\n\n  --log-level TEXT                The base console logging level. Can be\n                                  \'debug\', \'info\', \'warning\' and \'error\'.\n                                  [default: info]\n\n  --install-completion            Install completion for the current shell.\n  --show-completion               Show completion for the current shell, to\n                                  copy it or customize the installation.\n\n  --help                          Show this message and exit.\n```\n\nThe script will crawl files, extract exif and output visualizations named `insight_1.png` and `insight_2.png` in a newly created `outputs` folder (or a folder named as you specified).\n\n## Output example\n\nHere is an example of what the script outputs:\n\n![Example_1](example_outputs/insight_1.jpg)\n\n![Example_2](example_outputs/insight_2.jpg)\n\n## TODO\n\n- [x] Handling raw files.\n- [x] Handling subfolders when looking for files.\n- [x] Output all insight in a single/two plot.\n- [x] Implement proper logging.\n- [x] Make into a package.\n- [x] Make callable as a python module (`python -m photocrawl ...`).\n- [x] Improving the command line experience.\n\n---\n\n<div align="center">\n  <sub><strong>Made with ♥︎ by fsoubelet</strong></sub>\n  <br>\n  <sub><strong>MIT &copy 2019 Felix Soubelet</strong></sub>\n</div>\n\n\n[exiftool]: https://www.sno.phy.queensu.ca/~phil/exiftool/\n[license]: https://github.com/fsoubelet/PhotoCrawl/blob/master/LICENSE \n[pyexifinfo]: https://github.com/guinslym/pyexifinfo\n',
    'author': 'Felix Soubelet',
    'author_email': 'felix.soubelet@liverpool.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fsoubelet/PhotoCrawl',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
