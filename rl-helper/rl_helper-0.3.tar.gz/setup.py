from setuptools import find_packages, setup


# Required dependencies
required = [
    "gym","pytest","matplotlib","pyvirtualdisplay","pyyaml","attrdict"
]


setup(
    name='rl_helper',
    version="0.3",
    author="cywgoog@gmail.com",
    packages=find_packages(include=['rl_helper']),
    include_package_data=True,
    install_requires=required
)