from setuptools import setup, find_packages

VERSION = '1.0.1'
DESCRIPTION = 'Handling links'
LONG_DESCRIPTION = 'A package that allows to Handling links'

# Setting up
setup(
    name="gunlink",
    version=VERSION,
    author="Brijesh Krishna",
    author_email="brijeshkrishnaga@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=open('README.md').read(),
    packages=find_packages(),
    url='https://github.com/Brijeshkrishna/gunlink',
    license='MIT',
    install_requires=['numpy', 'ipwhois', 'pyshorteners', 'pydantic'],
    keywords=['gunlink','python', 'link', 'python3'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
