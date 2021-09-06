from setuptools import setup

'''
To upload:
python3 setup.py check
python3 setup.py sdist
twine upload dist/*
'''

setup(
    name='caph1993-posets',
    version='2.0.1',
    description='Toolbox for finite posets and lattices',
    url='https://github.com/caph1993/caph1993-posets',
    author='Carlos Pinzón',
    author_email='caph1993@gmail.com',
    license='MIT',
    packages=[
    	'cp93posets',
    ],
    install_requires=[
        'numpy',
        'caph1993-pytools',
        'pyhash',
        'pydotplus',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)