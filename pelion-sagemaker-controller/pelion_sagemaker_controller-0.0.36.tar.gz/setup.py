import pathlib
import os
from setuptools import setup

__version__ = '0.0.36'

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# pull our requirements
with open(os.path.join(HERE, 'requirements.txt')) as fh:
    requirements = fh.readlines()

# This call to setup() does all the work
setup(
    name="pelion_sagemaker_controller",
    description="AWS Sagemaker Controller notebook/client API for Pelion Edge Gateways",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/DougAnsonAtARM/pelion-sagemaker-controller",
    author="Doug Anson",
    author_email="Doug.Anson@pelion.com",
    license='Apache 2.0',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python',
        'Topic :: Internet',
    ),
    packages=['pelion_sagemaker_controller'],
    install_requires=requirements,
    python_requires='>=2.7.10, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.0, !=3.4.1, !=3.4.2, <4',
    version=__version__,
)
