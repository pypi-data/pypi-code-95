

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='airflow_customs_by_novigi',
    version="1.0.19",
    description='Novigi Custom Airflow operators, hooks and plugins',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT', 
    packages=['airflow_customs_by_novigi','airflow_customs_by_novigi.operators', 'airflow_customs_by_novigi.hooks', 'airflow_customs_by_novigi.custom_plugings'],
    install_requires=['requests','jsonpath_ng','pandas', 'pyodbc', 'psycopg2'],
    setup_requires=['setuptools', 'wheel'],
    author='Novigi',
    author_email='integration@novigi.com.au',
)
