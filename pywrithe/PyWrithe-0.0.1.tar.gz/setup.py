from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(name='PyWrithe',
      version='0.0.1',
      description='All Python package to compute writhe of closed curves with numpy or jax.numpy',
      url='https://github.com/RadostW/PyWrithe/',
      author='Radost Waszkiewicz',
      author_email='radost.waszkiewicz@gmail.com',
      long_description=long_description,
      long_description_content_type='text/markdown',  # This is important!
      project_urls = {
          'Documentation': 'https://pywrithe.readthedocs.io',
          'Source': 'https://github.com/RadostW/PyWrithe/'
      },
      license='MIT',
      packages=['pywrithe'],
      zip_safe=False)
