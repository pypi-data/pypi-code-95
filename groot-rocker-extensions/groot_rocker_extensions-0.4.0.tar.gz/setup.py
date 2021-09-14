#!/usr/bin/env python3

##############################################################################
# Imports
##############################################################################

import setuptools

##############################################################################
# Requirements
##############################################################################

install_requires = [
    # build
    'setuptools',
    # runtime
    'distro',
    'groot_rocker',
]

extras_require = {
    'tests': ['codecov', 'coverage', 'nose', 'pytest'],
    'packaging': ['stdeb', 'twine']
}

##############################################################################
# Setup
##############################################################################

d = setuptools.setup(
    name='groot_rocker_extensions',
    version='0.4.0',
    packages=setuptools.find_packages(exclude=['tests*', 'docs*']),
    package_data={'groot_rocker_extensions': ['templates/*.em', 'templates/*.bash']},
    install_requires=install_requires,
    extras_require=extras_require,
    author='Daniel Stonier',
    maintainer='Daniel Stonier <d.stonier@gmail.com>',
    url='http://github.com/stonier/groot_rocker_extensions',
    keywords=['Docker'],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries'
    ],
    description="groot_rocker extensions for groot workflows",
    long_description="A few groot_rocker extensiosn for groot workflows.",
    license='BSD',
    python_requires='>=3.0',
    entry_points={
        'console_scripts': [
            'groot-rocker-workspace = groot_rocker_extensions.main:main_workspace',
        ],
        'groot_rocker.extensions': [
            'bind = groot_rocker_extensions.bind:Bind',
            'colcon = groot_rocker_extensions.colcon:Colcon',
            'development_environment = groot_rocker_extensions.development_environment:DevelopmentEnvironment',
            'git = groot_rocker_extensions.git:Git',
            'named_prompt = groot_rocker_extensions.named_prompt:NamedPrompt',
            'nvidia = groot_rocker_extensions.nvidia:Nvidia',
            'pulse_audio = groot_rocker_extensions.pulse_audio:PulseAudio',
            'ssh = groot_rocker_extensions.ssh:Ssh',
            'user = groot_rocker_extensions.user:User',
            'work_directory = groot_rocker_extensions.work_directory:WorkDirectory',
        ],
    },
)
