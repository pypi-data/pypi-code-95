import setuptools

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().strip().split('\n')

setuptools.setup(
    name='miptlabs',
    version='1.0.9',
    author="Dmitry",
    description="The package will help MIPT students to draw graphs easier",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dimon58/miptlabs",
    project_urls={
        "Bug Tracker": "https://github.com/dimon58/miptlabs/issues",
    },
    data_files=[
        'readme.md',
        'requirements.txt'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=requirements
)
