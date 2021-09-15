import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='riotpy',
    version='0.0.2',
    author='Daniel Lee',
    author_email='tworiver1213@gmail.com',
    description='Package for Riot API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/header1213/riotpy',
    install_requires= ['requests'],
    packages=setuptools.find_packages(exclude = []),
    python_requires='>=3',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)