import setuptools
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
requirements = open(os.path.dirname(os.path.abspath(__file__)) + "/requirements.txt").read().splitlines()

setuptools.setup(
    name="nwdata",
    version="0.2",
    author="Mihai Cristian Pîrvu",
    author_email="mihaicristianpirvu@gmail.com",
    description="Generic Dataset Reader high level API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/neuralwrappers/nwdata",
    keywords = ["dataset", "reader", "high level api"],
    packages=setuptools.find_packages(),
    install_requires=requirements,
    license="WTFPL",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
