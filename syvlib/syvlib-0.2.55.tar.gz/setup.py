import os
from setuptools import setup

readme_path = os.path.join(
    os.path.realpath(os.path.dirname(__file__)),
    'README.md'
)

with open(readme_path, 'r') as stream:
    readme_content = stream.read()

setup(
    name='syvlib',
    version='0.2.55',
    description='Array codec and API wrapper for SYV server',
    long_description=readme_content,
    long_description_content_type='text/markdown',
    url='https://bitbucket.org/Thomas_Ash/syvlib/',
    author='Thomas Ash',
    author_email='syv.development@protonmail.com',
    license='GPL',
    packages=['syvlib'],
    zip_safe=True,
    install_requires=['numpy', 'requests']
)
