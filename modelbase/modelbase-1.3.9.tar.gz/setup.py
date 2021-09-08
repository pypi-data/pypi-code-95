# type: ignore

import codecs
import os
import pathlib
import re

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="modelbase",
    version=find_version("modelbase", "__init__.py"),
    description="A package to build metabolic models",
    long_description=(pathlib.Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://gitlab.com/ebenhoeh/modelbase",
    author="Oliver Ebenhoeh, Marvin van Aalst",
    author_email="oliver.ebenhoeh@hhu.de, marvin.van.aalst@hhu.de",
    maintainer_email="marvin.van.aalst@hhu.de, janina.mass@hhu.de, anna.matuszynska@hhu.de",
    license="GPL3",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS",
        "Operating System :: OS Independent",
    ],
    keywords="modelling ode metabolic",
    platforms="any",
    project_urls={
        "Documentation": "https://modelbase.readthedocs.io/en/latest/",
        "Source": "https://gitlab.com/ebenhoeh/modelbase",
        "Tracker": "https://gitlab.com/ebenhoeh/modelbase/issues",
    },
    packages=find_packages("."),
    package_data={"modelbase": ["py.typed"]},
    install_requires=[
        "dataclasses",
        "matplotlib",
        "numpy",
        "pandas",
        "python-libsbml",
        "scipy",
        "black==21.5b0",
        "sympy",
        "tqdm",
        "ipywidgets",
    ],
    python_requires=">=3.7.0",
    zip_safe=False,
)
