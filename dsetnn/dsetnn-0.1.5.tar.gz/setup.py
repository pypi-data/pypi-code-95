from setuptools import setup
import codecs
import os.path


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name='dsetnn',
    version=get_version("dsetnn/__init__.py"),    
    description='PyTorch implementation of the Differentiable Spatial to Ellipse Transform (DSET). Code extended from the official implementation of DSNT',
    url='https://gitlab.uni.lu/agarcia/dset-pytorch',
    author='Albert Garcia',
    author_email='albert.garcia@uni.lu',
    license='Apache License 2.0',
    packages=['dsetnn'],
    install_requires=['torch>=1.2.0',
                      'numpy',
                      'scipy',
                      'matplotlib'
                      ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: GPU :: NVIDIA CUDA :: 10.0',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Image Processing',
    ],
)
