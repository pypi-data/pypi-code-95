from setuptools import setup

VERSION = '0.0.3'
DESCRIPTION = 'Official Blaugue API package'
f = open('README.md')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name="blaugue",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author="CAMARM-DEV",
    author_email="armand@camponovo.xyz",
    license='MIT',
    packages=['blaugue'],
    install_requires=['requests~=2.25.1',
'Markdown~=3.3.4',
'setuptools~=57.0.0'],
    keywords='conversion',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3",
    ],
    long_description_content_type='text/markdown'
)
