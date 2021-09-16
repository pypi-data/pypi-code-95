
from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="IDEA_SESIT",
    version="0.0.1",
    author="Mark He",
    author_email="hexuanheng@gmail.com",
    description="Integrated Dashboard for Energy transition Analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
       "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    packages=find_packages(),
    python_requires=">=3.6",
)
