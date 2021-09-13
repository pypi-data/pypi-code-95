from setuptools import setup, find_packages
import os
import platform

lib_path = os.path.dirname(os.path.realpath(__file__))
requirements_path = os.path.join(lib_path, 'requirements.txt')

install_requires = [] 
if os.path.isfile(requirements_path):
    with open(requirements_path) as f:
        install_requires = f.read().splitlines()
        

system = platform.system()
if system == 'Linux':
    kubectl_binary = 'bin/linux/kubectl'
if system == 'Windows':
    kubectl_binary = 'bin/windows/kubectl.exe'

setup(
    name='iictl',
    version='0.0.1.2',
    description='integrated instance control command line tool',
    license='MIT',
    packages=[*find_packages()],
    author='Kim Minjong',
    author_email='caffeinism@estsoft.com',
    keywords=['kubernetes'],
    url='https://github.com/est-ai/iictl',
    entry_points = {
        'console_scripts': ['iictl=iictl.main:entrypoint'],
    },
#     package_data={'': [kubectl_binary]},
    include_package_data=True,
    install_requires=install_requires,
#     scripts=[kubectl_binary],
#     zip_safe=False,
)
