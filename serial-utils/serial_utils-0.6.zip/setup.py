import setuptools

#with open("README.md", "r") as fh:
#    long_description = fh.read()

setuptools.setup(
    name='serial_utils',    # This is the name of your PyPI-package.
    version='0.6',
    url='https://github.com/ryanGT/serial_utils',
    author='Ryan Krauss',
    author_email='ryanwkrauss@gmail.com',
    description="package for fascilitating serial communication between python and arduino",
    #long_description=long_description,
    #long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
