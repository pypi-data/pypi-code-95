import os, sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def main():
    setup(
        name='py_velocity_topology_parser',
        version= '0.1',
        author='Poornima Wari',
        author_email='poornima.wari@spirent.com',
        url='https://github.com/waripoornima/velocity_topology_parser',
        description='velocity_topology_parser: topology parser for .xml,.tbml or string',
        long_description = 'See https://github.com/waripoornima/velocity_topology_parser',
        license='http://www.opensource.org/licenses/mit-license.php',
        keywords='Velocity API',
        classifiers=['License :: OSI Approved :: MIT License',
                     'Operating System :: POSIX',
                     'Operating System :: Microsoft :: Windows',
                     'Operating System :: MacOS :: MacOS X',
                     'Topic :: Software Development :: Libraries',
                     'Topic :: Utilities',
                     'Programming Language :: Python',
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3'],
        packages=['py_velocity_topology_parser'],
        install_requires=['lxml>=4.6.3'],
        zip_safe=True,
        )


if __name__ == '__main__':
    main()
