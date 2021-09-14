import setuptools

with open('requirements.txt', encoding="utf-16") as f:
    requirements = f.readlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="control_scnu",
    # Replace with your own username
    version="0.2.2",
    author="lxy",
    author_email="2471974739@qq.com",
    description="A small example package20200805_lxy",
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='<=3.8',
    include_package_data=True,
)
