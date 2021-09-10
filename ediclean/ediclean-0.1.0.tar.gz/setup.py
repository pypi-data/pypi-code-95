from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='ediclean',
    version='0.1.0',
    description='Clean UN/EDIFACT PAXLST files from unsupported characters.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/goOICT/edicat',
    author='Zoltan Janota',
    author_email='zoltan.janota@un.org',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Text Processing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='paxlst edifact un/edifact',
    packages=['ediclean'],
    python_requires='>=3.8',
    install_requires=[''],
    entry_points={
        'console_scripts': [
            'ediclean = ediclean.__main__:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/goOICT/edicat/issues',
        'Source': 'https://github.com/goOICT/edicat',
    },
)
