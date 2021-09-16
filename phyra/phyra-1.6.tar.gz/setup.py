from setuptools import setup, find_packages
with open('README.md') as f:
    long_description = f.read()

def read_requirements():
    with open('requirements.txt', 'r') as req:
        content = req.read()
        requirements = content.split('\n')

    return requirements

setup(
    name='phyra',
    version='1.6',
    author='LyQuid',
    author_email='lyquidpersonal@gmail.com',
    description = 'A interactive CLI for programmer and everyone',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    entry_points="""
        [console_scripts]
        phyra=phyra.cli:cli
    """,
)
