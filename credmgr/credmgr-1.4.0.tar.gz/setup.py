import re
from os import path

from setuptools import find_packages, setup

project_name = "credmgr"

root = path.abspath(path.dirname(__file__))

with open(path.join(root, project_name, "const.py")) as f:
    __version__ = re.search(r'__version__ = "(.+)"', f.read()).group(1)

with open(path.join(root, "README.rst")) as f:
    long_description = f.read()

extras = {
    "docs": ["sphinx", "sphinx_rtd_theme"],
    "lint": [
        "black",
        "docstrfmt",
        "flake8",
        "flynt",
        "isort",
        "pydocstyle",
        "sphinx<3.0",
        "sphinx_rtd_theme",
    ],
    "test": [
        "betamax",
        "betamax_serializers",
        "coverage",
        "mock",
        "pytest",
        "pytest-cov",
        "pytest-mock",
        "pytest-xdist",
    ],
}
extras["dev"] = extras["docs"] + extras["lint"] + extras["test"]

requires = ["asyncpraw", "praw", "python-dateutil", "requests", "requests_toolbelt"]

setup(
    name=project_name,
    author="Lil_SpazJoekp",
    author_email="spaz@jesassn.org",
    license="Proprietary",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "License :: Other/Proprietary License",
    ],
    python_requires=">=3.6",
    description="Credential Manager API Client",
    include_package_data=True,
    install_requires=requires,
    long_description=long_description,
    package_data={"": ["LICENSE.txt"], project_name: ["*.ini"]},
    packages=find_packages(exclude=["tests", "tests.*"]),
    test_suite="tests",
    tests_require=extras["test"],
    extras_require=extras,
    url="https://credmgr.jesassn.org",
    version=__version__,
)
