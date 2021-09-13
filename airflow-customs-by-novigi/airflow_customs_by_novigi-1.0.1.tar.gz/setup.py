

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='airflow_customs_by_novigi',
    version="1.0.1",
    description='Novigi Custom Airflow operators, hooks and plugins',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT', 
    packages=find_packages(exclude=['tests']),
    install_requires=['requests','jsonpath_ng','pandas',],
    setup_requires=['setuptools', 'wheel'],
    author='Novigi',
    author_email='integration@novigi.com.au',
)
