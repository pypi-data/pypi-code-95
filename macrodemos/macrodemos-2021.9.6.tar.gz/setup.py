""" The macrodemos package setup.
Based on setuptools

Randall Romero-Aguilar, 2016-2021
"""

from setuptools import setup
from codecs import open


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='macrodemos',
    version='2021.09.06',
    description='Demos to learn macroeconomics and macro-econometrics concepts',
    long_description=long_description,
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



