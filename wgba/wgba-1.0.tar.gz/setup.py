from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
   name='wgba',
   version='1.0',
   python_requires='>3.6', 
   description='Which genome build again?',
   long_description=long_description,
   long_description_content_type="text/markdown",
   url="https://github.com/Chris1221/wgba",
   project_urls={
      "Bug Tracker": "https://github.com/Chris1221/wgba/issues",
      "Source": "https://github.com/Chris1221/wgba",
   },
   author='Chris Cole',
   author_email='ccole@well.ox.ac.uk',
   install_requires = ["pyBigWig", "pandas"],
   packages=['wgba', 'wgba.sizes'],  
   include_package_data = True,
   entry_points={
        'console_scripts': [
            'wgba = wgba.cli:cli',
        ],
    }
)