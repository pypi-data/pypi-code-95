from pathlib import Path

from setuptools import setup, find_packages

setup(
    name='avro-preprocessor',
    version_format='{tag}',
    description='A preprocessor for Avro Schemata',
    long_description=Path('README.md').read_text().replace("""![avropreprocessor](avro.jpg)""", ""),
    long_description_content_type='text/markdown',
    keywords=['avro', 'preprocessor', 'schema', 'schemas', 'schemata'],
    url='https://gitlab.com/Jaumo/avro-preprocessor',
    author='Jaumo GmbH',
    author_email='nicola.bova@jaumo.com',
    packages=find_packages(),
    scripts=['avro_preprocessor/avropreprocessor.py'],
    license='Apache2',
    install_requires=[
        'networkx==2.6.2',
        'pygments>=2.6.1',
        'requests==2.20.0',
        'ruamel.yaml==0.16.12',
        'ruamel.yaml.clib==0.2.2',
    ]
)
