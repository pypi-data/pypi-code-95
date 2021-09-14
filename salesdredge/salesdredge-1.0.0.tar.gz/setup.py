import pathlib
from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="salesdredge",
    version="1.0.0",
    description="This is the API for the Salesdredge.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="http://www.salesdredge.com",
    author="Christopher Roos",
    author_email="roos.christopher@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "salesdredge=salesdredge.__main__:main",
        ]
    },
)