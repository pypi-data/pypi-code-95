import setuptools


def get_readme():
    with open('README.rst') as f:
        return f.read()


setuptools.setup(
    # the first three fields are a must according to the documentation
    name="pytsv",
    version="0.1.67",
    packages=[
        'pytsv',
    ],
    # from here all is optional
    description="pytsv is a module to help with all things TSV",
    long_description=get_readme(),
    long_description_content_type="text/x-rst",
    author="Mark Veltzer",
    author_email="mark.veltzer@gmail.com",
    maintainer="Mark Veltzer",
    maintainer_email="mark.veltzer@gmail.com",
    keywords=[
        'python',
        'tsv',
        'format',
        'csv',
    ],
    url="https://veltzer.github.io/pytsv",
    download_url="https://github.com/veltzer/pytsv",
    license="MIT",
    platforms=[
        'python3',
    ],
    install_requires=[
        'pytconf',
        'tqdm',
        'pyanyzip',
        'numpy',
        'pandas',
        'pylogconf',
        'attrs',
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ],
    data_files=[
    ],
    entry_points={"console_scripts": [
        'pytsv=pytsv.main:main',
    ]},
    python_requires=">=3.6",
)
