import re

from setuptools import find_packages
from setuptools import setup

import versioneer

setup(
    name="git_version_info",
    packages=find_packages(),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Basic version tagging for python scripts and plots",
    install_requires=[
        r
        for r in open("requirements.in").read().splitlines()
        if r and not re.match(r"\s*\#", r[0])
    ],
    author="Charles Baynham",
    license="",
)
