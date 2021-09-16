

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='novigi_common',
    version="1.0.0",
    description='Novigi Custom Airflow operators, hooks and plugins',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT', 
    packages=['novigi_common','novigi_common.operators', 'novigi_common.hooks', 'novigi_common.custom_plugings'],
    install_requires=['requests','jsonpath_ng','pandas', 'pyodbc', 'psycopg2'],
    setup_requires=['setuptools', 'wheel'],
    author='Novigi',
    author_email='integration@novigi.com.au',
)
