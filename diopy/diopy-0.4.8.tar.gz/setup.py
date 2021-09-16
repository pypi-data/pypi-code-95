import glob, os
from setuptools import setup, find_packages

path = os.path.abspath(os.path.dirname(__file__))

try:
  with open(os.path.join(path, 'README.md')) as f:
    long_description = f.read()
except Exception as e:
  long_description = "The single cell data IO between R and Python(Python version)"
  

setup(
    name = "diopy",
    version = "0.4.8",
    keywords = ["scRNA-seq", "hdf5", "data IO", "scanpy"],
    description = "The single cell data IO between R and Python(Python version)",
    long_description = long_description,
    long_description_content_type='text/markdown',
    python_requires=">=3.5.0",
    license = "MIT License",
    author = "Huijian Feng",
    author_email = "fenghuijian@outlook.com",
    packages = find_packages(),
    include_package_data = True,
    # If any package contains *.r files, include them:
    package_data={'': ['*.R']},
    requires = ["scipy", "scanpy","pandas", "numpy", "anndata","re","os","h5py","typing", "argparse"],
    platforms = "any",
    # packages=['diopy'],
    scripts = ['bin/scdior']
)
