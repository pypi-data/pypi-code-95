from setuptools import setup, find_packages

VERSION = '0.1'
DESCRIPTION = 'Math and artificial intelligence tools'

# Setting up
setup(
    name="intelligen",
    version=VERSION,
    author="Bouchet07 (Diego Bouchet)",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['numpy'],
    keywords=['python', 'AI', 'math', 'artificial', 'intelligence'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)