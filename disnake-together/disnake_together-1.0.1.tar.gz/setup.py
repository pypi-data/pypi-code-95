from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Natural Language :: English',
    'Topic :: Internet',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='disnake_together',
    version='1.0.1',
    description="A 3rd party library to use discord's VC Party Games feature with disnake",
    long_description="A 3rd party library to use discord's VC Party Games feature i.e YouTube together, "
                     "Betrayal.io, Fishington.io, Chess in the park, Poker night",
    url='https://github.com/awesomehet2124/disnake_together',
    author='Het Naik',
    author_email='awesomehet@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords=['disnake_together', 'disnake', 'disnake-vc-interactions'],
    packages=find_packages(),
    install_requires=['aiohttp']
)
