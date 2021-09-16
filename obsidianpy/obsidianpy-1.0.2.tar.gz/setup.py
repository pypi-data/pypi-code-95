import setuptools

with open("README.md") as f:
    readme = f.read()


setuptools.setup(
    name="obsidianpy",
    author="cloudwithax",
    version="1.0.2",
    url="https://github.com/cloudwithax/obsidian.py",
    packages=setuptools.find_packages(),
    license="GPL",
    description="A discord.py ready wrapper for the audio sending node, Obsidian",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=['discord.py>=1.7.1'],
    extra_require=None,
    classifiers=[
        "Framework :: AsyncIO",
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries',
        "Topic :: Internet"
    ],
    python_requires='>=3.8',
    keywords=['obsidian', 'obsidian.py', "discord.py"],
)