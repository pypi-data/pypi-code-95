import setuptools


def get_readme():
    with open('README.rst') as f:
        return f.read()


setuptools.setup(
    # the first three fields are a must according to the documentation
    name="pytconf",
    version="0.0.74",
    packages=[
        'pytconf',
    ],
    # from here all is optional
    description="pytconf handles configuration and command line parsing",
    long_description=get_readme(),
    long_description_content_type="text/x-rst",
    author="Mark Veltzer",
    author_email="mark.veltzer@gmail.com",
    maintainer="Mark Veltzer",
    maintainer_email="mark.veltzer@gmail.com",
    keywords=[
        'click',
        'argparse',
        'optparse',
        'command-line-parser',
        'configuration',
    ],
    url="https://veltzer.github.io/pytconf",
    download_url="https://github.com/veltzer/pytconf",
    license="MIT",
    platforms=[
        'python3',
    ],
    install_requires=[
        'colored',
        'yattag',
        'pyfakeuse',
    ],
    extras_require={
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ],
    data_files=[
    ],
    entry_points={"console_scripts": [
    ]},
    python_requires=">=3.7",
)
