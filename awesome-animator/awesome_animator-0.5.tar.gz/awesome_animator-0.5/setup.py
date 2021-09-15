
from setuptools import setup, find_packages

setup(
    name = 'awesome_animator',
    packages = find_packages(),
    version = '0.5',
    license = 'MIT',
    description = 'It\'s awesome, it\'s animator, it\'s awesome animator',
    install_requires= [
        'matplotlib',
        'numpy'
    ]
)
