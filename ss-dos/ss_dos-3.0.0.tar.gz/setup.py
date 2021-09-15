import setuptools

setuptools.setup(
    name="ss_dos",
    version="3.0.0",
    author="enygames",
    description="fix some problems",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
