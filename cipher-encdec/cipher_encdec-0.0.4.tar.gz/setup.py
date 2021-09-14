from setuptools import setup, find_packages

VERSION = '0.0.4'
DESCRIPTION = 'Encodes and Decodes your Data'
LONG_DESCRIPTION = 'A package that allows to Encode and Decode your Data the way you want.'

# Setting up
setup(
    name="cipher_encdec",
    version=VERSION,
    author="Cipher_Secure",
    # author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'cipher'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)