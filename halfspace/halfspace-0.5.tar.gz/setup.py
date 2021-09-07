from setuptools import setup

setup(
    name="halfspace",
    version="0.5",
    author="Andreas Sogaard",
    author_email="as@halfspace.io",
    description=("Core Halfspace python library"),
    keywords="halfspace",
    url="https://halfspace.ai/",
    packages=['halfspace'],
    install_requires=[
        'matplotlib',
        'seaborn'
    ]
)
