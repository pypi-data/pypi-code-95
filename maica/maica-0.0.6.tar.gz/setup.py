import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='maica',
    version='0.0.6',
    author='Gyoung S. Na',
    author_email='ngs0@krict.re.kr',
    description='Python package for chemical machine learning.',
    keywords='chemical science, materials science, artificial intelligence, machine learning',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
)
