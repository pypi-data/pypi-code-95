import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
name="aristoteDash",
version="1.2.2",
author="Dorian Drevon",
author_email="drevondorian@gmail.com",
description="Programme de prévision de production électrique d'une centrale PV",
long_description=long_description,
long_description_content_type="text/markdown",
classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
],
# packages=setuptools.find_packages(),
packages=['aristoteDash'],
# packages=setuptools.find_packages(exclude=["quickTest"]),
package_data={'': ['confFiles/*']},
# include_package_data=True,
install_requires=['dorianUtilsModulaire==3.6.1','geopy==2.2.0','tzwhere==3.0.3'],
python_requires=">=3.8"
)
