from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='tracardi-local-timespan',
    version='0.1.2',
    description='The purpose of this plugin is to check if current time is in given time span.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Marcin Gaca',
    author_email='emygeq@gmail.com',
    packages=['tracardi_local_timespan'],
    install_requires=[
        'pydantic',
        'tracardi_dot_notation',
        'tracardi-plugin-sdk',
        'pytz'
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