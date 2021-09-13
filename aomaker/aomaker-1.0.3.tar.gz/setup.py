import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aomaker",
    version="1.0.3",
    author="ancientone",
    author_email="listeningsss@163.com",
    description="An api testing framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ae86sen/aomaker",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'Faker',
        'Jinja2',
        'jsonpath',
        'loguru',
        'PyMySQL',
        'pytest',
        'pytest-tmreport',
        'PyYAML',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'amake=aomaker.cli:main_make_alias',
            'arun=aomaker.cli:main_arun_alias',
            'aomaker=aomaker.cli:main',
        ]
    }
)
