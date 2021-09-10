from setuptools import setup, find_packages

with open("README.md", "r") as stream:
    long_description = stream.read()

setup(
    name = 'botamino_new.py',
    version = '3.0',
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
        'ThePhoenix78',
        'AminoBot',
        'BotAmino',
        'botamino',
        'aminobot',
        'python3.x',
        'slimakoi',
        'official'
    ],
    install_requires = [
        'schedule',
        'setuptools',
        'requests',
        'reportlab',
        'websocket-client==0.57.0',
        'argparse',
        'amino_new.py'
    ],
    setup_requires = [
        'wheel'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    packages = find_packages()
)
