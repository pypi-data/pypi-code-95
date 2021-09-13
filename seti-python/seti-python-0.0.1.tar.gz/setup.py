from distutils.core import setup
import setuptools


setup(
    name='seti-python',
    version='0.0.1',
    include_package_data=True,
    description='Library to use conect to seti functions',
    author='Andres Gonzalez',
    author_email='andres@4coders.co',
    license="GPLv3",
    # use the URL to the github repo
    url='https://github.com/4CodersColombia/seti-python',
    download_url='https://github.com/4CodersColombia/seti-python/archive/refs/tags/0.0.1.tar.gz',
    keywords=['python'],
    classifiers=['Programming Language :: Python :: 3.9', ],
    packages=setuptools.find_packages(),
    install_requires=[
        'PyExecJS==1.5.1',
        'pycryptodome==3.10.1'
    ],
)
