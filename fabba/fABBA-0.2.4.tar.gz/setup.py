import setuptools
from pathlib import Path
from setuptools import Extension
from Cython.Build import cythonize
from distutils.command.build import build as build_orig
import numpy

with open("README.md", 'r') as f:
    long_description = f.read()

caggregation = Extension('fABBA.caggregation',
                          sources=['fABBA/caggregation.pyx'], include_dirs=["fABBA"])
caggregation_memview = Extension('fABBA.caggregation_memview',
                             sources=['fABBA/caggregation_memview.pyx'], include_dirs=["fABBA"])
chainApproximation_c = Extension('fABBA.chainApproximation_c',
                             sources=['fABBA/chainApproximation_c.pyx'], include_dirs=["fABBA"])
class build(build_orig):

    def finalize_options(self):
        super().finalize_options()
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        for extension in self.distribution.ext_modules:
            extension.include_dirs.append(numpy.get_include())
        from Cython.Build import cythonize
        self.distribution.ext_modules = cythonize(self.distribution.ext_modules,
                                                  language_level=3)
setuptools.setup(
    name="fABBA",
    packages=setuptools.find_packages(),
    version="0.2.4",
    setup_requires=["cython", "numpy"],
    cmdclass={"build": build},
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
