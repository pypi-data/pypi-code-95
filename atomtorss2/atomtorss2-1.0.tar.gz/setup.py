from distutils.core import setup


LONG_DESCRIPTION = """
ATOM to RSS2

Released under MIT Licence.
"""

setup(
    name='atomtorss2',
    version='1.0',
    packages=['atomtorss2'],
    url='https://github.com/flrt/atom_to_rss2',
    license='MIT',
    keywords="Atom,feed,XML",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    author='Frederic Laurent',
    author_email='frederic.laurent@gmail.com',

    description='Atom to rss2 converter',
    long_description=LONG_DESCRIPTION
)
