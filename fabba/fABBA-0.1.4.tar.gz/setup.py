import setuptools
from pathlib import Path
from Cython.Build import cythonize
import numpy

# this_directory = Path(__file__).parent
# long_description = (this_directory / "RELEASE.md").read_text()

# with open("RELEASE.md", "r") as fh:
#  long_description = fh.read()
  
setuptools.setup(
    name="fABBA",
    packages=['fABBA'],
    version="0.1.4",
    ext_modules=cythonize(["fABBA/caggregation.pyx", 
                           "fABBA/caggregation_memview.pyx", 
                           "fABBA/chainApproximation_c.pyx"]), 
    include_dirs=[numpy.get_include()],
    long_description="RELEASE.md",
    author="Stefan Guettel, Xinye Chen",
    author_email="stefan.guettel@manchester.ac.uk",
    description="An efficient aggregation based symbolic representation",
    long_description_content_type='text/markdown',
    url="https://github.com/nla-group/fABBA",
    # packages=setuptools.find_packages(),
    install_requires=['numpy'],
    license='BSD 3-Clause'
)