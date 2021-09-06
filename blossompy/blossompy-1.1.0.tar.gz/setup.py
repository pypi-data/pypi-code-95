import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='blossompy',
    version='1.1.0',
    ##packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='Used to run and create basic commands for Human-Robot Interaction with the Blossom Robot',
    long_description_content_type="text/markdown",
    long_description=open('./blossompy/README.md').read(),
    #entry_points={
    #    "console_scripts": [
    #        "blossompy=start:main",
    #    ]
    #},
    install_requires=['PyQt5','py-getch','getch','opencv-python==4.3.0.38','simpleaudio','PyYAML','flask_cors','prettytable','flask_cors','PyYAML','simpleaudio','opencv-python==4.3.0.38','getch','py-getch','PyQt5'],
    url='https://github.com/riya-ranjan/blossom-public/tree/master/blossompy',
    author='Riya Ranjan',
    package_data={'blossompy': ['*.json']},
    packages=find_packages(exclude=("tests",)),
    author_email='riya.ranjan.00@gmail.com',
    include_package_data=True
)
