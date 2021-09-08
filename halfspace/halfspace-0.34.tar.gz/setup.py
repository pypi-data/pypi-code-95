from setuptools import setup
from glob import glob

setup(
    name="halfspace",
    version="0.34",
    author="Andreas Sogaard",
    author_email="as@halfspace.io",
    description=("Core Halfspace python library"),
    keywords="halfspace",
    include_package_data=True,
    url="https://halfspace.ai/",
    packages=['halfspace'],
    install_requires=[
        'matplotlib',
        'seaborn'
    ]
)
