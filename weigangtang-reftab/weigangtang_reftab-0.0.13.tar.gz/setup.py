from setuptools import setup, find_packages

readme = open('README.md').read()
changelog = open('CHANGELOG.md').read()
long_description = '\n\n'.join([readme, changelog])

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: OS Independent ',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='weigangtang_reftab',
    version='0.0.13',
    description='manage journal reference',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    author='Weigang (Victor) Tang',
    author_email='tangw5@mcmaster.ca',
    license='MIT',
    classifiers=classifiers,
    keywords='basic, reference manager',
    packages=find_packages(),
    install_requires=['numpy', 'pandas', 'tabulate'],
)