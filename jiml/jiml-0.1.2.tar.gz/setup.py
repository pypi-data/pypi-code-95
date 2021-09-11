from distutils.core import setup
from pathlib import Path

this_directory = Path(__file__).parent

long_description = (this_directory / "README.md").read_text()


setup(
    name='jiml',
    packages=['jiml'],
    version='0.1.2',
    license='MIT',
    description='Convert json to json using jinja2 and yaml',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Vladimir',
    author_email='vmstarchenko@edu.hse.ru',
    url='https://github.com/vmstarchenko/jiml',
    keywords=['json2json', 'json', 'yaml', 'template'],
    install_requires=[
        'PyYAML',
        'Jinja2',
        'jinja-vanish',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    zip_safe=True,
)
