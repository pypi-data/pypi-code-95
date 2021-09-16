import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    cleaned = ""
    for line in long_description.split('\n'):
        if '[![Build Status]' in line:
            pass
        elif '[![codecov]' in line:
            pass
        else:
            cleaned += line + "\n"
    long_description = cleaned

setuptools.setup(
    name="easysparql",  # Replace with your own username
    version="1.5.2",
    author="Ahmad Alobaid",
    author_email="aalobaid@fi.upm.es",
    description="A python wrapper to easily query knowledge graphs with SPARQL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oeg-upm/easysparql",
    packages=setuptools.find_packages(),
    install_requires=[
        'SPARQLWrapper',
    ],
    classifiers=[
        # "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
