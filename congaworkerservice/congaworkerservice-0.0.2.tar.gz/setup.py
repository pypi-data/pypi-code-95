from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["pip>=21.2.4", "wheel>=0.37.0", "pika>=1.2.0"]

setup(
    name="congaworkerservice",
    version="0.0.2",
    author="Nikola Markovic",
    author_email="nmarkovic@conga.com",
    description="A package to interact with queue message broker",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/nmarkovic-conga/conga-worker-service/",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)