from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]


def readme():
    return open('README.md').read()


setup(
    name='Bitkub-Api',
    version='0.0.14',
    description='A Non-official very basic Bitkub API',
    long_description=readme(),
    long_description_content_type="text/markdown",
    url='https://github.com/l3oatkunGG/bitkub-api',
    author='',
    author_email='',
    license='MIT',
    classifiers=classifiers,
    keywords='Bitkub api',
    packages=find_packages(),
    install_requires=['requests']
)