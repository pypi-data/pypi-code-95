import os

from setuptools import setup
from setuptools import find_packages

PYPI_PACKAGE_VERSION = os.environ.get("PYPI_PACKAGE_VERSION", "dev")


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


long_description = read("README.md")

setup(
    name="coco-sdk",
    version=PYPI_PACKAGE_VERSION,
    description="CoCo(Conversational Components) SDK for building modular chatbots",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Chen Buskilla",
    author_email="chen@buskilla.com",
    url="https://github.com/conversationalcomponents/coco-sdk-py",
    license="MIT",
    install_requires=["requests", "pygments", "pydantic", "lxml"],
    extras_require={"async": ["httpx"]},
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    python_requires=">=3.6",
)
