import subprocess
import setuptools
import sys
from datetime import datetime

def git_hash():
    try:
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode()[:-1] + ", "
    except:
        return ""

try:
    from conans import client
except ImportError:
    subprocess.call([sys.executable, '-m', 'pip', 'install', 'conan'])
    from conans import client

try:
    from skbuild import setup
except ImportError:
    subprocess.call([sys.executable, '-m', 'pip', 'install', 'scikit-build'])
    from skbuild import setup

with open('README.md', 'r') as file:
    long_description = file.read()

setup_requirements = [
    'scikit-build>=0.11.1',
    'cmake>=3.16',
    'conan>=1.25',
]

__version__ = '0.1'

setup (
    name = 'kbw',
    version=__version__,
    cmake_source_dir='.',
    cmake_args=[
        '-DCMAKE_BUILD_TYPE=Release',
        f'-DKBW_BUILD_INFO="{__version__} ({git_hash()}{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")})"',
    ],
    author='Evandro Chagas Ribeiro da Rosa',
    author_email='evandro.crr@posgrad.ufsc.br',
    description='Ket Bitwise Simulator Server.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/quantum-ket/kbw',
    license='Apache-2.0',
    packages=setuptools.find_namespace_packages(include=['kbw', 'kbw.*']),
    setup_requires=setup_requirements,
    install_requires=['flask>=2', 'gevent>=21.1.2'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: C++',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
    ],
    entry_points={'console_scripts': ['kbw = kbw.__main__:main']},
)
