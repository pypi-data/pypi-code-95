from distutils.core import setup
from pathlib import Path
this_directory = Path(__file__).parent
print(this_directory)
long_description = (this_directory / "README.rst").read_text()
setup(
  name = 'BodyFatCalculator',         # How you named your package folder (MyLib)
  packages = ['BodyFatCalculator'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'First Custom Lib on pip',   # Give a short description about your library
  long_description=long_description,
  long_description_content_type='text/markdown',
  author = 'Juber Gandharv',                   # Type in your name
  author_email = 'juber269@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/JuberGandharv/BodyFat_Lib',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/JuberGandharv/Custom_lib_body_fat/archive/refs/tags/V0.1.tar.gz',    # I explain this later on
  keywords = ['BodyFat, Fat percentage, bodyfat calculator'],   # Keywords that define your package best
  install_requires=[],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
