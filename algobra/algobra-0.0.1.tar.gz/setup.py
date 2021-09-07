from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="algobra",
    version="0.0.1",
    description="Python Algorithimic Trading Engine",
    py_modules=["engine"],
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
    url="https://twitter.com/bradleycm4",
    author="Chris Bradley",
    author_email="declarationcb@gmail.com",
    extras_require={"dev": ["pytest>=3.7", "twine"]},
)
