from setuptools import setup, find_packages
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="amc-cropper",
    version="0.0.5",
    description="Crops AMC files to descired length based on provided fps, start, and end whole seconds. Works through command line.",
    long_description_content_type="text/markdown",
    long_description=README,
    packages=find_packages(include=["amccrop","amccrop.*"]),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries",
    ],
    url="https://github.com/UomoCaffeLatte/AMCCrop",
    author="Nikhil Reji",
    author_email="Nikhil.Reji@live.co.uk",
    install_requires=["AsfAmc-Parser"],
    entry_points={
        "console_scripts": [
            "amccrop=amccrop.__main__:main",
        ]
    },
)