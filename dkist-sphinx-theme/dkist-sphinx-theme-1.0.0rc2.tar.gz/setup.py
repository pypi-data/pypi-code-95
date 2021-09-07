
from setuptools import setup

setup(
    name="dkist-sphinx-theme",
    description="The sphinx theme for DKKST.",
    long_description="The documentation theme for projects related to the DKIST DC and Telescope.",
    author="AURA/NSO",
    setup_requires="setuptools_scm",
    install_requires=[
        "setuptools",
        "sphinx-bootstrap-theme"
    ],
    packages=['dkist_sphinx_theme'],
    include_package_data=True,
    use_scm_version=True,
)
