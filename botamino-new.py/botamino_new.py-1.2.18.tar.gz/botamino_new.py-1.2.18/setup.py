from setuptools import setup, find_packages

with open("README.md", "r") as stream:
    long_description = stream.read()

setup(
    name = 'botamino_new.py',
    version = '1.2.18',
    url = 'https://github.com/aminobot22/MAmino.py',
    download_url = 'https://github.com/aminobot22/MAmino.py.git',
    license = 'MIT',
    author = 'phoenix meliods',
    author_email = 'parttimer57@gmail.com',
    description = 'A library to create Amino bots.',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    keywords = [
        'aminoapps',
        'amino_new-py',
        'amino',
        'amino-bot',
        'narvii',
        'api',
        'python',
        'python3',
        'python3.x',
        'slimakoi',
        'official'
    ],
    install_requires = [
        'schedule',
        'requests',
        'reportlab',
        'websocket-client==0.57.0',
        'argparse',
        'amino_new.py'
    ],
    setup_requires = [
        'wheel'
    ],
    packages = find_packages()
)
