from setuptools import setup,find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="raser",
    version="2.0.1",
    author="Xin Shi",
    author_email="xin.shi@outlook.com",
    description="Simulate timing resolution, TCT, TPA-TCT of 2D&3D Si&SiC detector",
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