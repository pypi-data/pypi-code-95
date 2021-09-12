import setuptools

_requires = [
    'six',
    'appdirs',
    'setuptools-scm',
    'fastapi',
    'python-multipart',
    'python-jose[cryptography]',
    'passlib[bcrypt]',
    'aiofiles',
    'uvicorn',
    'loguru',
    'wpasupplicantconf',
]

setuptools.setup(
    name='ebs-linuxnode-netconfig',
    url='',

    author='Chintalagiri Shashank',
    author_email='shashank.chintalagiri@gmail.com',

    description='Network configuration infrastructure for embedded linux nodes',
    long_description='',

    packages=setuptools.find_packages(),
    package_dir={'ebs.linuxnode.netconfig': 'ebs/linuxnode/netconfig'},
    package_data={'ebs.linuxnode.netconfig': ['static/*.*',
                                              'static/static/css/*.*',
                                              'static/static/js/*.*',
                                              'static/static/media/*.*']},

    install_requires=_requires,
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux',
    ],
    entry_points={
          'console_scripts': [
              'netconfig = ebs.linuxnode.netconfig.server:run_server'
          ]
    },
)
