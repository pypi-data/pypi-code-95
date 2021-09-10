import setuptools
from pathlib import Path
from setuptools import Extension
from Cython.Build import cythonize
import numpy

with open("README.md", 'r') as f:
    long_description = f.read()

caggregation = Extension('fABBA.caggregation',
                          sources=['fABBA/caggregation.pyx'])
caggregation_memview = Extension('fABBA.caggregation_memview',
                             sources=['fABBA/caggregation_memview.pyx'])
chainApproximation_c = Extension('fABBA.chainApproximation_c',
                             sources=['fABBA/chainApproximation_c.pyx'])
                             
setuptools.setup(
    name="fABBA",
    packages=setuptools.find_packages(),
    version="0.2.2",
    ext_modules=cythonize([caggregation, caggregation_memview, chainApproximation_c]), 
    include_dirs=[numpy.get_include()],
    long_description=long_description,
    author="Stefan Guettel, Xinye Chen",
    author_email="stefan.guettel@manchester.ac.uk",
    description="An efficient aggregation based symbolic representation",
    long_description_content_type='text/markdown',
    url="https://github.com/nla-group/fABBA",
    install_requires=['numpy'],
    license='BSD 3-Clause'
)
