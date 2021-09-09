import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="citibox-gcloud-logger",  # Replace with your own username
    version="0.4.6-rc1",
    author="Citibox",
    description="Citibox Google cloud logging tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://citibox.com",
    packages=setuptools.find_namespace_packages(include=["citibox.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
