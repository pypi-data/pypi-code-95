from setuptools import setup,find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="raser",
    version="0.2",
    author="Xin Shi",
    author_email="XXX@example.com",
    description="Simulate timing resolution of 2D&3D SiC&Si detector",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dt-np/raser",
    packages=find_packages(),
    classifiers=[
				"Programming Language :: Python :: 3",
				"License :: OSI Approved :: MIT License",
				"Operating System :: OS Independent",
    			]
)