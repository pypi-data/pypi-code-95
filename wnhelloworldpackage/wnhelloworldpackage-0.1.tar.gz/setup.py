import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='wnhelloworldpackage',
    version='0.1',
    author="Witold Netel",
    author_email="wnetel901@gmail.com",
    description="hello world!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wnetel/helloworld",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
 )