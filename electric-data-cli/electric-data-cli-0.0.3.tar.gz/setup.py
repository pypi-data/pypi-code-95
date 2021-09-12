from setuptools import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except ImportError:
    with open('README.md') as f:
        long_description = f.read().strip()

with open('VERSION') as f:
    version = f.read().strip()

setup(
    name='electric-data-cli',
    description='Electric Data command line interface utility.',
    long_description=long_description,
    url='https://github.com/electric-data/electric-cli',
    author='Electric Data',
    author_email='info@electricdata.net',
    version=version,
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
      'click>=7',
      'durations>=0.3',
      'requests>=2',
    ],
    python_requires='>=3.5',
    zip_safe=False,
    entry_points = {
        'console_scripts': [
            'electric = electric.main:cli',
        ],
    },
)
