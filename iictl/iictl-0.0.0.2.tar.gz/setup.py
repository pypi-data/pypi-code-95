from setuptools import setup, find_packages
import os

lib_path = os.path.dirname(os.path.realpath(__file__))
requirements_path = os.path.join(lib_path, 'requirements.txt')

install_requires = [] 
if os.path.isfile(requirements_path):
    with open(requirements_path) as f:
        install_requires = f.read().splitlines()
setup(
    name='iictl',
    version='0.0.0.2',
    description='integrated instance control command line tool',
    license='MIT',
    packages=find_packages(),
    author='Kim Minjong',
    author_email='caffeinism@estsoft.com',
    keywords=['kubernetes'],
    url='https://github.com/est-ai/iictl',
    entry_points = {
        'console_scripts': ['iictl=iictl.main:entrypoint'],
    },
    install_requires=install_requires,
)
