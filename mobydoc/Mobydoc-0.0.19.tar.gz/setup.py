from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = "Mobydoc",
    version = "0.0.19",
    author = "Raphaël Jacquot",
    author_email = "raphael.jacquot@univ-grenoble-alpes.fr",
    description = "SqlAlchemy mapper to mobydoc database",
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    package_dir = {'':'src'},
    packages = find_namespace_packages('src'),
    python_requires='>=3.7',
    project_urls = {
        
    }
)
