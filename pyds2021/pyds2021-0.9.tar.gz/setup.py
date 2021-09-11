from distutils.core import setup
setup(
  name = 'pyds2021',         # How you named your package folder (MyLib)
  packages = ['pyds2021'],   # Chose the same as "name"
  version = '0.9',      # Start with a small number and increase it with every change you make
  license='Harvard',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description='A Python 3 library for the 2021 univ.ai pyds course',# Give a short description about your library
  author = 'Univ.ai',                   # Type in your name
  author_email = 'hnjoy@mac.com',      # Type in your E-Mail
  url = 'https://github.com/blindedjoy/',   # Provide either the link to your github or to your website
  #download_url = 'https://github.com/blindedjoy/RcTorch/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['pyds2021'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'numpy',
          'seaborn',
          'sklearn',
          'datetime',
          'pandas',
          'seaborn',
          'matplotlib',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.6',
  ],

)