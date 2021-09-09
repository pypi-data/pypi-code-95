# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['matchms_plotly']

package_data = \
{'': ['*']}

install_requires = \
['matchms>=0.9.0,<0.10.0',
 'numpy>=1.20.0,<2.0.0',
 'pandas>=1.2.1,<2.0.0',
 'plotly>=4.14.3,<5.0.0',
 'pytest-cov>=2.12.1,<3.0.0']

setup_kwargs = {
    'name': 'matchms-plotly',
    'version': '0.1.3',
    'description': 'Plot Matchms spectra with Plotly].',
    'long_description': '# matchms-plotly\n\nPlot [Matchms](https://matchms.readthedocs.io) spectra with [Plotly](https://plotly.com/python/).\n\nThis package is under developement for the [MetWork](www.metwork.science) project.\n\n## Install\n\n```bash\npip install matchms-plotly\n```\n\n## Usage\n\n```python\nfrom matchms_plotly import plot_spectrum, plot_spectra\n\n# Plot a single spectrum.\nplot_spectrum(spectrum)\n\n# Plot two spectrums in the "up and down" fashion.\nplot_spectra(spectrum_up, spectrum_down)\n```\n',
    'author': 'Yann Beauxis',
    'author_email': 'dev@yannbeauxis.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/metwork/libs/matchms-plotly',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
