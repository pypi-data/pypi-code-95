from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='tracardi-mysql-connector',
    version='0.1.3',
    description='The purpose of this plugin is to connect with mysql database',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Risto Kowaczewski',
    author_email='risto.kowaczewski@gmail.com',
    packages=['tracardi_mysql_connector'],
    install_requires=[
        'aiomysql',
        'pydantic',
        'tracardi-plugin-sdk',
        'tracardi>=0.6.10'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=['tracardi', 'plugin'],
    python_requires=">=3.8",
    include_package_data=True
)