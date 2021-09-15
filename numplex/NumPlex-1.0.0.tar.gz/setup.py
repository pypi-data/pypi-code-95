import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="NumPlex",
    version="1.0.0",
    author="Physictype",
    description="Complex numbers compatable with numpy",
    long_description=long_description, # don't touch this, this is your README.md
    long_description_content_type="text/markdown",
    url="https://replit.com/@DatM314/NumPlex",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)