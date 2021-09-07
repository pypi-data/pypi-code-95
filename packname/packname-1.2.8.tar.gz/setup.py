from distutils.core import setup
import setuptools

setup(
  name = 'packname',         # How you named your package folder (MyLib)
  packages = ['packname', 'packname/subm_a', 'packname/subm_b'],   # Chose the same as "name"
  #packages=setuptools.find_packages(where="packname"),
  version = '1.2.8',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'blablabla',   # Give a short description about your library
  author = 'Fra',                   # Type in your name
  author_email = 'your.email@domain.com',      # Type in your E-Mail
  url = 'https://github.com/fgabbaninililly/TestPyPiUpload',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/fgabbaninililly/TestPyPiUpload/archive/refs/tags/1.2.5.tar.gz',    # I explain this later on
  keywords = ['SOME', 'MEANINGFULL', 'KEYWORDS'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'numpy'
      ],
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
  package_dir={"": "."},

  python_requires=">=3.6",
)