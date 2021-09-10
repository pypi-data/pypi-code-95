from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as README:
    long_description = README.read()

classifiers = [
    'Development Status :: 1 - Planning',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Topic :: Scientific/Engineering',
]

setup(
    author='Saketh Chandra',
    author_email='b.sakethchandra9@gmail.com',
    name="QuantumRNG",
    version="0.0.1",
    # packages=find_packages(),
    install_requires=["qiskit"],
    python_requires=">=3.6",
    classifiers=classifiers,
    license='BSD',
    description='Quantum Random Number Generator Using One Qubit',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Saketh-Chandra/QuantumRNG',
    keywords=['qiskit', 'quantum', 'random number generator', 'qrng', 'rng', 'planning'],
)
