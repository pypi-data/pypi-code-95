import setuptools

REQUIREMENTS_FILE = "requirements.txt"

with open(REQUIREMENTS_FILE, "r") as f:
    required = f.read().splitlines()

package_name = "bds_courseware"

setuptools.setup(
    name=package_name,
    version="1.1.0",
    install_requires=required,
    packages=setuptools.find_packages(),
    description="Dataset utilities for EPAM Data Science basic course",
)
