import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
name="smarthyesDash",
version="1.5",
author="Dorian Drevon",
author_email="drevondorian@gmail.com",
description="source codes and config Files to monitor smarthyes data",
long_description=long_description,
long_description_content_type="text/markdown",
# url="https://github.com/pypa/sampleproject",
# project_urls={
#     "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
# },
classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
],
# packages=setuptools.find_packages(),
packages=['smarthyesDash'],
# packages=setuptools.find_packages(exclude=["quickTest"]),
package_data={'': ['confFiles/*']},
include_package_data=True,
install_requires=['dorianUtilsModulaire==3.6.1'],
python_requires=">=3.8"
)
