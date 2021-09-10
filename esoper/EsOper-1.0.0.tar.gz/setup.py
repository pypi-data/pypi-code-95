from setuptools import setup
from os import path

DIR = path.dirname(path.abspath(__file__))
INSTALL_PACKAGES = open(path.join(DIR, 'requirements.txt')).read().splitlines()

with open(path.join(DIR, 'README.md')) as f:
    README = f.read()

setup(
    name='EsOper',
    packages=['esoper'],
    description="Elastic Search Operator by httpx",
    long_description=README,
    long_description_content_type='text/markdown',
    install_requires=INSTALL_PACKAGES,
    version='1.0.0',
    url='https://github.com/wdf618/ESOper',
    author='Dingfeng Wu',
    author_email='94050502@qq.com',
    keywords=['Elastic', 'Elastic Search', 'httpx'],
    tests_require=['testEsOper.py'],
    include_package_data=False,
    python_requires='>=3'
)