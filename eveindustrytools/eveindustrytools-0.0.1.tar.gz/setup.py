from distutils.core import setup
setup(
  name = 'eveindustrytools',         
  packages = ['eveindustrytools'],   
  version = '0.0.1',      
  license='MIT',        
  description = 'provides a variety of functions useful for doing industry in eve online using evemarkettools',  
  author = 'Filip Jöde',                   
  author_email = 'joede.filip@gmail.com',      
  url = 'https://https://github.com/SustainedCruelty/eveindustrytools',  
  keywords = ['EVE Online', 'API', 'EVE ESI','Swagger'], 
  install_requires=['evemarkettools',
					'pandas',],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
