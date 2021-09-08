import setuptools

with open('README.md', 'r', encoding='UTF-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="BaseCore",
    version="0.0.1rc1",
    author="BaseCore",
    author_email="basecls@megvii.com",
    description="BaseCore",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MegEngine",
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: C++',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    license='Apache 2.0',
    keywords='MegEngine classification'
)
