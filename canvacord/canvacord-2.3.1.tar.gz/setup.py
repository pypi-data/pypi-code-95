from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_desc = open("C:/Users/runne/OneDrive/Desktop/Bot Projects/CanvacordPy/canvacord.py/README.md", "r")
long_description = long_desc.read()
versionfile = open("C:/Users/runne/OneDrive/Desktop/Bot Projects/CanvacordPy/canvacord.py/version.txt", "r")
content = versionfile.read()
version = str(content)
version = version.split('.')
versionnumber1 = version[0]
versionnumber2 = version[1]
versionnumber3 = version[2]
versionnumberint1 = int(versionnumber1)
versionnumberint2 = int(versionnumber2)
versionnumberint3 = int(versionnumber3)
versionnumberint1 = versionnumberint1 + 1
if versionnumberint1 > 9:
    versionnumberint1 = 0
    versionnumberint2 = versionnumberint2 + 1
if versionnumberint2 > 9:
    versionnumberint2 = 0
    versionnumberint1 = 0
    versionnumberint3 = versionnumberint3 + 1
version = str(versionnumberint3) + '.' + str(versionnumberint2) + '.' + str(versionnumberint1)
versionfile = open("C:/Users/runne/OneDrive/Desktop/Bot Projects/CanvacordPy/canvacord.py/version.txt", "w")
versionfile.truncate(0)
versionfile.write(version)
versionfile.close()

setup(
    name='canvacord',
    version=version,
    description='A Python Version of Canvacord',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/BlazenBoi/canvacord.py/issues',
    author='Blazen',
    author_email='contact@fireballbot.com',
    keywords='canvacord, rankcard, image manipulation, meme, discord, discordpy, discord-py',
    packages=find_packages(include=['canvacord']),
    python_requires='>=3.6',
    install_requires=[
    "setuptools>=42",
    "wheel",
    "pillow",
    "discord",
    "asyncio",
    "aiohttp",
    "typing",
    "datetime"
    ],
    project_urls={
        'Discord Server': 'https://discord.com/invite/mPU3HybBs9',
        'Bug Tracker': 'https://github.com/BlazenBoi/canvacord.py/issues',
        'Source': 'https://github.com/BlazenBoi/canvacord',
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
      ]
)
#© 2021 GitHub, Inc.