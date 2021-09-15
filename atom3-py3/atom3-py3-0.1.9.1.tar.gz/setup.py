from setuptools import setup

setup(
    name='atom3-py3',
    packages=['atom3'],
    url='https://github.com/amorehead/atom3',
    version='0.1.9.1',
    description='3D Atomic Data Processing (Python 3 version)',
    long_description=open("README.rst").read(),
    author='Raphael Townshend',
    license='MIT',
    install_requires=[
        'biopython',
        'click',
        'easy-parallel-py3',
        'h5py',
        'pandas>=0.24.0',
        'scipy',
    ],
    entry_points={
        'console_scripts': [
            "atom3 = atom3.main:main",
        ]
    }
)
