""" The macrodemos package setup.
Based on setuptools

Randall Romero-Aguilar, 2016-2021
"""

from setuptools import setup
from codecs import open
from pathlib import Path
import sys


CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))  # for setuptools.build_meta


def get_long_description():
    return (CURRENT_DIR / "README.md").read_text(encoding='utf-8')

setup(
    name='macrodemos',
    version='2021.09.07',
    description='Demo programs to learn macroeconomics and macro-econometrics concepts',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Randall Romero-Aguilar',
    author_email='randall.romero@outlook.com',
    url='http://randall-romero.com/code/macrodemos',
    license='MIT',
    keywords='time series, ARMA, filters, Markov chain, Solow-Swan, Hodrick-Prescott, Baxter-King',
    packages=['macrodemos'],
    python_requires='>=3.7',
    install_requires=['pandas', 'numpy', 'plotly', 'dash', 'statsmodels>=0.12', 'jupyter-dash'],
    include_package_data=True,
    package_data={'macrodemos': ['macrodemos/data/IFS_GDP.xlsx', 'macrodemos/data/CRI-initial-data.pickle']}
)



