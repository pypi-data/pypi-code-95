#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = []
import os
cont = os.listdir('.')
print(os.getcwd())
print('Contents:', cont)
with open('requirements.txt') as f:
    for line in f:
        stripped = line.split("#")[0].strip()
        if len(stripped) > 0:
            requirements.append(stripped)

setup_requirements = [ ]

test_requirements = [ ]

setup(
    name='nucleaizer_backend',
    author="Ervin Tasnadi",
    author_email='tasnadi.ervin@brc.hu',
    python_requires='>=3.6',
    description='Backend for the napari_nucleaizer plugin',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='nucleaizer_backend',
    packages=[
        'nucleaizer_backend', 
        'nucleaizer_backend.CycleGAN', 
        'nucleaizer_backend.mrcnn_interface', 
        'nucleaizer_backend.Mask_RCNN_tf2',
        'nucleaizer_backend.Mask_RCNN_tf2.mrcnn',
        'nucleaizer_backend.pix2pix_interface',
        ],
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/etasnadi/nucleaizer_backend',
    version='0.1.6',
    zip_safe=False,
)
