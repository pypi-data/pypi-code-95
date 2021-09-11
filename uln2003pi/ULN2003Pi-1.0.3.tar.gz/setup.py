from distutils.core import setup
setup(
  name = 'ULN2003Pi',         # How you named your package folder (MyLib)
  packages = ['ULN2003Pi'],   # Chose the same as "name"
  version = '1.0.3',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Package to control a ULN2003 driver for a 28BYJ-48 (or any unipolar) stepper motor on a Raspberry Pi',   # Give a short description about your library
  author = 'Ryan Parker',                   # Type in your name
  author_email = 'rap71@cam.ac.uk',      # Type in your E-Mail
  #url = 'https://github.com/user/reponame',   # Provide either the link to your github or to your website
  #download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['ULN2003', '28BYJ-48', 'Stepper', 'Motor', 'Stepper-motor', 'Stepper motor'],   # Keywords that define your package best
  classifiers=[
    'Development Status :: 5 - Production/Stable',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ]
)