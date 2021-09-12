"""
Setup.py for module micomp.
"""

from setuptools import setup, find_packages  # Always prefer setuptools over distutils


def get_long_description():
    with open('README.md', 'r') as fh:
        return fh.read()


setup(
    name='amqp_framework',
    version='0.1.1',
    description='Awesome producers and consumers powered by aio_pika.',
    long_description=get_long_description(),
    license='MIT',

    # The project's main homepage.
    url='https://github.com/aobcvr/amqp_framework',

    # Author details
    author='aobcvr',
    author_email='aobcvr@gmail.com',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        'Programming Language :: Python :: 3',

        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.9',

    # What does your project relate to?
    keywords='amqp aio_pika',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(),
    install_requires=[
        'aio-pika==6.8',
        'marshmallow',
        'environs',
    ],
    extras_require={
        'dev': [
            # Linters
            'isort==5.9.3',
            # Static analyse
            'flake8==3.9.2',
        ]
    }
)
