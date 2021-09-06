from setuptools import setup

VERSION = "0.0.10"

def readme():
    """print long description"""
    with open("README.md", "r") as fh:
        return fh.read()

setup(
    name="erix-python-utils",
    version=VERSION,
    author="Eric Stratigakis",
    author_email="enstrati@uwaterloo.ca",
    description="All of my utilities and tools in one place",
    py_modules=["homebrew"],
    package_dir={"":"src"},
    classifiers=[
        "Development Status :: 1 - Planning",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    long_description=readme(),
    long_description_content_type="text/markdown",
    install_requires=["requests"],
    python_requires='>=3',
)