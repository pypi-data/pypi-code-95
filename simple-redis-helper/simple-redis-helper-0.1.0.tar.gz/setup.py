from setuptools import setup


def _read(f):
    """
    Reads in the content of the file.
    :param f: the file to read
    :type f: str
    :return: the content
    :rtype: str
    """
    return open(f, 'rb').read()


setup(
    name="simple-redis-helper",
    description="Command-line utilities to for sending/receiving data to/from a Redis backend.",
    long_description=(
        _read('DESCRIPTION.rst') + b'\n' +
        _read('CHANGES.rst')).decode('utf-8'),
    url="https://github.com/fracpete/redis_helper",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python :: 3',
    ],
    license='MIT License',
    package_dir={
        '': 'src'
    },
    packages=[
      'simple_redis_helper',
    ],
    version="0.1.0",
    author='Peter Reutemann',
    author_email='fracpete@waikato.ac.nz',
    install_requires=[
        "redis",
    ],
    entry_points={
        "console_scripts": [
            "srh-load=simple_redis_helper.load:sys_main",
            "srh-save=simple_redis_helper.save:sys_main",
            "srh-broadcast=simple_redis_helper.broadcast:sys_main",
            "srh-listen=simple_redis_helper.listen:sys_main",
        ]
    }
)
