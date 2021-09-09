import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jama-client-CERTIC",
    version="0.0.17",
    author="Mickaël Desfrênes",
    author_email="mickael.desfrenes@unicaen.fr",
    description="Jama client library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.unicaen.fr/certic/jama-python-client",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests", "argh"],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": ["jama-cli=jama_client.__main__:run_cli"],
    },
)
