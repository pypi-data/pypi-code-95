from setuptools import setup
import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="django-secret-parametrizer", # Replace with your own username
    version="0.0.2",
    author="Diogo Berti",
    author_email="diogoberti88@gmail.com",
    description="Keep your secrtes on the DB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)