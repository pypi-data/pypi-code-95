from setuptools import setup
setup(
    name='crawler_test',
    version='0.1.1',
    license='MIT',
    description='This is a web application that extracts images URLs from web pages.',

    author='Amal Boukhdhir',
    author_email='boukhdhiramal@yahoo.fr',
    url='',
    packages=['crawler'],

    install_requires=['Scrapy', 'scrapyd', 'Flask']
)