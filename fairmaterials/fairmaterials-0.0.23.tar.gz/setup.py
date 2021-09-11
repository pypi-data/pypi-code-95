from setuptools import setup, find_packages

setup(
    name='fairmaterials',
    version='0.0.23',
    keywords=['FAIRification','PowerPlant','Engineering'],
    description='Build a json file based on FAIRification standard',
    long_description='The fairmaterials is a tool for fairing data. It reads a template JSON file to get the preset data. The user can fill the data by manually inputting or by importing a csv file. The final output will be a new JSON file with the same structure.',
    url='https://engineering.case.edu/centers/sdle/',
    author='Roger French, LiangyiHuang, Will Oltjen',
    author_email='roger.french@case.edu, lxh442@case.edu, wco3@case.edu',
    packages=find_packages(),
)