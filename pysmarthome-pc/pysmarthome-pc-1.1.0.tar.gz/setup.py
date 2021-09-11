from setuptools import setup, find_packages

setup(
    name='pysmarthome-pc',
    description='Pc plugin for pysmarthome',
    version='1.1.0',
    author='Filipe Alves',
    author_email='filipe.alvesdefernando@gmail.com',
    install_requires=[
        'pysmarthome~=2.2',
        'requests',
        'wakeonlan',
    ],
    packages=find_packages(),
    url='https://github.com/filipealvesdef/pysmarthome-pc',
    zip_zafe=False,
)
