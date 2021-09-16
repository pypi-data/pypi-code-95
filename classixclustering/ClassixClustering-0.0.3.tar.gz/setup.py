import setuptools
from Cython.Build import cythonize
import numpy

with open("README.md", 'r') as f:
    long_description = f.read()

setuptools.setup(
    name="ClassixClustering",
    packages=["ClassixClustering"],
    version="0.0.3",
    setup_requires=["cython>=0.29.4", "numpy>=1.20.0", "scipy>1.6.0"],
    install_requires=["numpy>=1.20.0", "tqdm", "pandas", "matplotlib"],
    ext_modules=cythonize(["ClassixClustering/*.pyx"], include_path=["ClassixClustering"]),
    package_data={"ClassixClustering": ["aggregation_cm.pyx", "amalgamation_cm.pyx"]},
    include_dirs=[numpy.get_include()],
    long_description=long_description,
    author="Stefan Guettel, Xinye Chen",
    author_email="stefan.guettel@manchester.ac.uk",
    description="Fast and explainable clustering",
    long_description_content_type='text/markdown',
    url="https://github.com/nla-group/CLASSIX",
    license='BSD 3-Clause'
)
