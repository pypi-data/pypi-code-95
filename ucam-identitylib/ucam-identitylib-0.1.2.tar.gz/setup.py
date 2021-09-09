import os

from setuptools import setup, find_packages


PACKAGE_NAME = "ucam-identitylib"
PACKAGE_DESCRIPTION = (
    "A module containing helpers and shared code related to identity systems within UIS, "
    "University of Cambridge."
)
PACKAGE_VERSION = "0.1.2"
PACKAGE_URL = "https://gitlab.developers.cam.ac.uk/uis/devops/iam/identity-lib"


def load_requirements(file: str):
    """
    Load requirements file and return non-empty, non-comment lines with leading and trailing
    whitespace stripped.
    """
    with open(os.path.join(os.path.dirname(__file__), file)) as f:
        return [
            line.strip() for line in f
            if line.strip() != '' and not line.strip().startswith('#')
        ]


with open("README.md") as readme_file:
    long_description = readme_file.read()

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    author="University of Cambridge Information Services",
    author_email=f"devops+{PACKAGE_NAME}@uis.cam.ac.uk",
    description=PACKAGE_DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url=PACKAGE_URL,
    packages=find_packages(),
    install_requires=load_requirements('requirements.txt'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
