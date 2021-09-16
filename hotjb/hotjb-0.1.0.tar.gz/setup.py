import setuptools

with open('readme.md', 'r', encoding='utf8') as reader:
    long_description = reader.read()

setuptools.setup(
    name='hotjb',
    version='0.1.0',
    description='yet a hotjb client.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='chaosannals',
    author_email='chaosannals@outlook.com',
    url='https://github.com/chaosannals',
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=[
        'aiohttp==3.7.4.post0',
    ],
)