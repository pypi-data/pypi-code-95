from setuptools import setup, find_packages
import os

# Setting up
setup(
    name="pandoraPlugintools",
    version="0.0.1",
    author="PandoraFMS projects department",
    author_email="<projects@pandorafms.com>",
    description="A pluguin tool set of functions for pandorafms",
    packages=find_packages(),
    zip_safe=False,
    install_requires=['datetime', 'psutil', 'requests', 'requests_ntlm'],
    keywords=['python', 'pandora', 'pandorafms', 'plugintool', 'plugintools'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
    ]
)