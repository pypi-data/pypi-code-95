
import setuptools
from setuptools import setup, find_packages
import codecs
import os
here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, "Readme.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()
setup(
    name='ARAMBHML',
    version='0.1.6',
    description='An Auto ML framework that solves Classification Tasks',
    author= 'Amartya Bhattacharya,Rupam Kumar Roy',
   
    long_description = long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    keywords=['auto ml','python' ,'classification problem', 'machine learning'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
   # python_requires='>=3.6',
  #  py_modules=['ARAMBHML'],
  #  package_dir={'':'src'},
    install_requires = [
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'scikit-learn',
        'sklearn-pandas',
        'xgboost',
        'plotly',
        'plotly-express'
    ]
)
