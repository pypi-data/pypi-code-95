from setuptools import setup

extras_require = {
    'discord': [
        'discord.py'
    ]
}

setup(
    name='IsDigit',
    url='https://github.com/editid0/IsDigit',
    author='editid',
    packages=['isdigit'],
    version='0.0.8',
    extras_require=extras_require,
    python_requires='>=3.8.0',
    license='MIT',
    description='Simple, mainly useless, python package that checks if a string, int, or float is a digit.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    keywords='python isdigit float int string'
)