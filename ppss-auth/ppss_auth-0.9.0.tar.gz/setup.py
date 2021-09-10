from setuptools import setup,find_packages


import os
here = os.path.abspath(os.path.dirname(__file__))
readme = open(os.path.join(here, 'README.md'), 'r').read()
changelog = open(os.path.join(here, 'README.md'), 'r').read()

setup(name='ppss_auth',
  version='0.9.0',
  description='simple auth scheme for pyramid, based on Mako template and sqlalchemy backend',
  long_description=readme + "\n\n\n" + changelog,
  long_description_content_type="text/markdown",
  author='pdepmcp',
  author_email='d.cariboni@pingpongstars.it',
  license='MIT',
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Framework :: Pyramid',
    'Topic :: Internet :: WWW/HTTP :: Session',
    'Programming Language :: Python :: 3.6',
  ],
  keywords="pyramid module authentication accelerator",
  python_requires='>=3.6',
  url='https://bitbucket.org/pingpongstars/ppss_auth/src/master/',
  install_requires=['pyramid_mako','pyramid_beaker','pyramid_jinja2','alembic' ],
  #packages=['src/test1'],
  packages=find_packages(),
  include_package_data=True,
  entry_points={
    'console_scripts': [
            'initialize_ppss_auth_db=ppss_auth.scripts.initialize_db:main',
            'ppss_auth_upgrade_db=ppss_auth.scripts.upgrade_db:main',
            'sayauth=ppss_auth.scripts.sayauth:sayitnow',
            'ppss_auth_cleanup_db=ppss_auth.scripts.cleanup_db:main',
            'ppss_auth_create_user=ppss_auth.scripts.create_user:create',
            'ppss_auth_update_user=ppss_auth.scripts.create_user:update',
    ],
  }

)


