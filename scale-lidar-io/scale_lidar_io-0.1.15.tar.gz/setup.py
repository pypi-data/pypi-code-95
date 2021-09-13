import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

setuptools.setup(
    name="scale_lidar_io",
    version="0.1.15",
    author="Scale AI",
    author_email="rodrigo.belfiore@scale.com",
    description="Lidar data conversion helpers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["scale_lidar_io"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=required,
)
