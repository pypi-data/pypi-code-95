from distutils.core import setup
setup(
    name='texttab',
    packages=['texttab'],
    version='0.5.1',
    license='MIT',
    description='Create ASCII tables that are flexible. Colours, various border styles and custom column formatters are some of the features.',   # Give a short description about your library
    author='Owen Klan',
    author_email='owen.j.klan@gmail.com',
    url='https://github.com/owenjklan/texttab',
    download_url='https://github.com/owenjklan/texttab/archive/refs/tags/v0.5.1.tar.gz',
    keywords=['command-line', 'ascii', 'tables', 'formatters', 'extensible'],
    install_requires=[
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        # Because we heavily use f-strings, a python 3.6 feature
        'Programming Language :: Python :: 3.6',
    ],
)