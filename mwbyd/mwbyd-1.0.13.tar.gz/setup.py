import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='mwbyd',
    version='v1.0.13',
    author='kts168',
    author_email='kts168@163.com',
    description="哈哈哈",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/kts168/mwbyd",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)