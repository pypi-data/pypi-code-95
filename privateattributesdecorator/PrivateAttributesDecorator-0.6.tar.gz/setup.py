from distutils.core import setup
setup(
  name = 'PrivateAttributesDecorator',         # How you named your package folder (MyLib)
  packages = ['PrivateAttributesDecorator'],   # Chose the same as "name"
  version = '0.6',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Module to increase encapsulation in Python, not allowing the access to private members outside their classes',   # Give a short description about your library
  long_description = 'Module to increase encapsulation in Python, not allowing the access to private members outside their classes. '
                     ''
                     'We offer a decorator that we can use to decorate a class for this purpose. We only have to include the parameters '
                     'we want to make private and if we want to allow for deep copies of objects of this class: '
                     ''
                     '@private_attributes_decorator.private_attributes_dec("arg1",allow_deep_copy=True)'
                     ''
                     'That way we won´t be able to get or set any our already private attributes plus the attribute arg1. '
                     'However, we will allow for deep copies of objects of that class',
  author = 'Antonio Pérez',                   # Type in your name
  author_email = 'ingovanpe@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/AntoData',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/AntoData/PrivateAttributesProject/archive/refs/tags/v0.6.tar.gz',    # I explain this later on
  keywords = ['Python', 'Python3', 'Encapsulation','Attributes','Private','Decorators'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9'
  ],
)