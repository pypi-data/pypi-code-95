from setuptools import setup
from setuptools_rust import Binding, RustExtension


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name="pyruvate",
    version="1.1.0",
    description="WSGI server implemented in Rust.",
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Rust",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
    ],
    keywords='WSGI',
    author='tschorr',
    author_email='t_schorr@gmx.de',
    url='https://gitlab.com/tschorr/pyruvate',
    rust_extensions=[
        RustExtension(
            "pyruvate.pyruvate",
            binding=Binding.RustCPython,
            debug=False,
            native=False)],
    packages=["pyruvate"],
    # rust extensions are not zip safe, just like C-extensions.
    zip_safe=False,
    install_requires=[
    ],
    extras_require={
        'test': [
            'pytest',
            'requests',
            ]},
    entry_points={
        'paste.server_runner': [
            'main=pyruvate:serve_paste',
        ],
    },
)
