from setuptools import setup, find_packages

setup(
    name='fairmaterials',
    version='0.0.24',
    keywords=['FAIRification','PowerPlant','Engineering'],
    description='Build a json file based on FAIRification standard',
    long_description='The fairmaterials is a tool for fairing data. It reads a template JSON file to get the preset data. The user can fill the data by manually inputting or by importing a csv file. The final output will be a new JSON file with the same structure.',
    url='https://engineering.case.edu/centers/sdle/',
    author='Roger French(ORCID:000000-0002-6162-0532), Liangyi Huang(ORCID:0000-0003-0845-3293), Will Oltjen,Arafath Nihar, Jiqi Liu(ORCiD: 0000-0003-2016-4160), Justin Glynn, Kehley Coleman',
    author_email='roger.french@case.edu, lxh442@case.edu, wco3@case.edu,axn392@case.edu,jxl1763@case.edu,jpg90@case.edu, kac196@case.edu',
    packages=find_packages(),
)