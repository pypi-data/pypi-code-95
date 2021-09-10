import setuptools
exec(open('navigation_mdp/_version.py').read())

# Ref: https://packaging.python.org/tutorials/packaging-projects/

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="navigation_mdp",
    version=__version__,
    author="Yagnesh Revar",
    author_email="mailto.yagnesh+github@gmail.com",
    description="A lightweight library for defining navigation grid world",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yrevar/navigation_mdp",
    packages=setuptools.find_packages(),
    keywords = ['Markov Decision Process', 'MDP', 'Navigation'],
    install_requires = [
        'navigation_vis'
    ],
    dependency_links=[
        'git+ssh://git@github.com/yrevar/navigation_vis@v0.8#egg=navigation_vis-0.9'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
