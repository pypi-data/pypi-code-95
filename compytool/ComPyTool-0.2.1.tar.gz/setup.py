from distutils.core import setup
setup(
  name = 'ComPyTool',         # How you named your package folder (MyLib)
  packages = ['ComPyTool'],   # Chose the same as "name"
  version = '0.2.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'A python based tool to compare .bam and .vcf files using SQLite3 database',   # Give a short description about your library
  author = 'Oliver Kutz',                   # Type in your name
  author_email = 'oliver.kutz@uniklinikum-dresden.de',      # Type in your E-Mail
  url = 'https://github.com/KutzO/ComPy',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/KutzO/ComPy/archive/refs/tags/_v021.tar.gz',    # I explain this later on
  keywords = ['genomics', 'sequencing', 'qc'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'python >=3.6',
          'matplotlib >=3.3',
          'pandas >=1.2',
          'pip >=20.3',
          'pypdf2 >=1.26',
          'pysam >=0.15',
          'seaborn >=0.11',
          'tqdm >=4.55',
          'xlsxwriter >=1.3',
          'pyyaml >=5.4',
          'numpy >=1.19'      
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
