

import setuptools
from setuptools import setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name='APIFNLIB',
    author='AquazDev',
    version="1.0.1",
    author_email=' ',
    description="Python LIB for FN-api.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=['FN-LIb', 'fnapi.com', 'fortnite', 'fortnite cosmetics', 'Fn-api', 'Fnapi.com'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3",
    install_requires=[""],
)