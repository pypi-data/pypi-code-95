from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

keywords = ['validator', 'mobile', 'number']

setup(
    name = 'mobilenumvalidator',
    version = '0.0.2',
    description = 'A basic Australian mobile number validation',
    long_description = open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url = '',
    author = 'Ajay Ganapathy',
    author_email = 'iajay543@gmail.com',
    license = 'MIT',
    classifiers = classifiers,
    keywords = keywords,
    packages = find_packages(),
    install_requires = ['']
)