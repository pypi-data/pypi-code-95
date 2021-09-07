from codecs     import open
from inspect    import getsource
from os.path    import abspath, dirname, join
from setuptools import (find_packages, setup)

here = abspath(dirname(getsource(lambda:0)))

with open(join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(  # Finally, pass this all along to distutils to do the heavy lifting.
    name="multiploit",
    author="YEETEDWIN",
    version='1.1.2.3',
    author_email="yeetedwin@protonmail.com",
    url="https://yeetedwin.is-a.dev/multiploit",
    download_url="https://yeetedwin.is-a.dev/multiploit/installing.html",
    project_urls={
        'Documentation': 'https://yeetedwin.gitbook.io/multiploit/',
        'Installation': 'https://yeetedwin.gitbook.io/multiploit/',
        'Source Code': 'https://github.com/YEETEDWIN/multiploit',
        'Bug Tracker': 'https://github.com/YEETEDWIN/multiploit/issues'
    },
    description      = "A python multi-purpose package",
    long_description = long_description,
    long_description_content_type="text/x-rst",
    license="MIT",
    platforms="any",
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Natural Language :: English',
        'Topic :: Software Development',
        'Topic :: Education :: Testing',
    ],
    keywords='multi-purpose multi simple one easier multiploit',
    install_requires=[
        "playsound>=1.3.0",
    ],
      packages=find_packages(exclude=["test"]),
    )
