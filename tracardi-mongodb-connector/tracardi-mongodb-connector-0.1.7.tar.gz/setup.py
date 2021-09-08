from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='tracardi-mongodb-connector',
    version='0.1.7',
    description='The purpose of this plugin is to connect to mongo and retrieve data.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Risto Kowaczewski',
    author_email='risto.kowaczewski@gmail.com',
    packages=['tracardi_mongodb_connector'],
    install_requires=[
        'tracardi_plugin_sdk>=0.6.8',
        'pydantic',
        'tracardi>=0.6.5',
        'motor~=2.5.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    keywords=['tracardi', 'plugin'],
    include_package_data=True,
    python_requires=">=3.8",
)
