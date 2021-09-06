import pathlib
from setuptools import setup,find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="pyresdev",
    version="0.0.104",
    description="Bairesdev package used in DS",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Patricio Massaro",
    author_email="patricio.massaro@bairesdev.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["numpy", "pandas", "regex","sqlalchemy","pymysql"],
)
