from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pyportall",
    author="Daniel Carrión",
    author_email="dcarrion@inspide.com",
    description="Portall Python SDK",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="0.0.9",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    install_requires=[
        'pydantic>=1.6.1',
        'httpx>=0.15.5',
        'geopandas'
    ]
)
