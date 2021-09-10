from setuptools import setup
import setuptools


with open("README.md", "r") as f:
    ld = f.read()


setup(
    name="ccp2_sdk",
    version="0.0.1",
    author="cyclone",
    description="ccp2 serverless sdk",
    long_description=ld,
    packages=setuptools.find_packages(),
    install_requires=[
        "requests",
    ]
)
