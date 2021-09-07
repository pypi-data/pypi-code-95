from setuptools import setup, find_packages

VERSION = "0.0.1"
DESCRIPTION = "Quandri Library-Merlin"
LONG_DESCRIPTION = "Quandri's Library for application"

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="q_merlin",
    version=VERSION,
    author="Matthew Ebert",
    author_email="ebertmx@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    package_dir={"": str("q_merlin")},
    # packages=find_packages(),
    # install_requires=["selenium"],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'
    keywords=["python", "package", "quandri", "q_merlin", "Merlin"],
    classifiers=[
        "Development Status :: 3 - Alpha",
    ],
)
