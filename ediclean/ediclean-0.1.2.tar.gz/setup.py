from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='ediclean',
    version='0.1.2',
    description='A Python package to strip non-standard text blocks from UN/EDIFACT messages.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/janotaz/ediclean',
    author='Zoltan Janota',
    author_email='zoltan.janota@un.org',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Text Processing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='paxlst edifact un/edifact',
    packages=['ediclean'],
    python_requires='>=3.4',
    install_requires=[''],
    entry_points={
        'console_scripts': [
            'ediclean = ediclean.__main__:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/janotaz/ediclean/issues',
        'Source': 'https://github.com/janotaz/ediclean',
    },
)
