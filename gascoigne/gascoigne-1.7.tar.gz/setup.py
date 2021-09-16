from distutils.core import setup
setup(
  name = 'gascoigne',         # How you named your package folder (MyLib)
  packages = ['gascoigne'],   # Chose the same as "name"
  version = '1.7',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'package with different tools',   # Give a short description about your library
  author = 'Gabriele Pinto',                   # Type in your name
  author_email = 'gabriele.pinto@uniroma1.it',      # Type in your E-Mail
  url = 'https://github.com/gabrielepinto/gascoigne',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/gabrielepinto/gascoigne/archive/refs/tags/1.7.tar.gz',    # I explain this later on
  keywords = ['coefficient plot', 'regression coefficient', 'coeffplot',"regression coefficient plot"],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
'matplotlib',
          'numpy',
          "pandas",
          "pdfplumber",
          "pdf2image",
          "pytesseract",
          "langdetect",
          "language_tool_python",
          "requests"
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
)