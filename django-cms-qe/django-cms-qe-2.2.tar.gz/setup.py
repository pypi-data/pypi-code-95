#!/usr/bin/env python3

import os

import setuptools


if __name__ == '__main__':
    readme_filename = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(readme_filename, encoding='utf-8') as readme_file:
        readme = readme_file.read()
    setuptools.setup(
        name='django-cms-qe',
        version='2.2',
        packages=setuptools.find_packages(exclude=[
            '*.tests',
            '*.tests.*',
            'tests.*',
            'tests',
            'test_utils.*',
            'test_utils',
            '*.migrations',
            '*.migrations.*',
        ]),
        include_package_data=True,
        description=(
            'Django CMS Quick & Easy provides all important modules to run new page without'
            'a lot of coding. Aims to do it very easily and securely.'
        ),
        long_description=readme,
        url='https://websites.pages.nic.cz/django-cms-qe',
        author='CZ.NIC, z.s.p.o.',
        author_email='kontakt@nic.cz',
        license='BSD License',

        python_requires='>=3.6',  # Aldryn forms 5.0,4 does not support Python 3.5.
        # All versions are fixed just for case. Once in while try to check for new versions.
        install_requires=[
            'django-filer==2.0.2',
            'aldryn-forms==5.0.4',  # Version aldryn-forms > 5.0.4 is compatible only with python 3.7.
            'Django==2.2.13',
            'aldryn-boilerplates==0.8.0',
            'argon2-cffi==20.1.0',
            'djangocms-file==2.4.0',
            'djangocms-link==2.6.1',
            'djangocms-picture==2.4.0',
            'django-axes==4.5.4',
            'django-bootstrap-form==3.4',
            'django-cms==3.7.4',
            'django-constance[database]==2.7.0',
            'django-csp==3.6',
            'django-import-export==2.2.0',
            'django-ipware==2.1.0',  # django-ipware==3.0.0 raises ModuleNotFoundError: No module named 'ipware.ip2'
            'django-tablib==3.2',  # Used by django-import-export
            'django-jsonfield==1.4.0',
            'django-mail-queue==3.2.4',
            'django-settings==1.3.12',
            'django-picklefield==3.0.1',
            'djangocms-bootstrap4==1.6.0',
            'djangocms-googlemap==1.4.0',
            'djangocms-text-ckeditor==3.9.1',
            'djangocms-attributes-field==1.2.0',  # Used by cms-qe-video
            'easy-thumbnails==2.7',  # Used by Django Filer
            'mailchimp3==3.0.14',
            'django-mptt==0.11.0',
            'python-memcached==1.59',
            'pytz',
            'typed_ast>1.4.0',  # 1.4.0 is required for python 3.8
        ],
        # Do not use test_require or build_require, because then it's not installed and is
        # able to be used only by setup.py util. We want to use it manually.
        # Actually it could be all in dev-requirements.txt but it's good to have it here
        # next to run dependencies and have it separated by purposes.
        extras_require={
            'dev': [
                'django-debug-toolbar==2.2',
                'django-extensions==2.2.9',
            ],
            'test': [
                'mypy',
                'pylint',
                'pylint-django',
                'pytest==5.4.3',
                'pytest-data==0.4',
                'pytest-django==3.9.0',
                'pytest-env==0.6.2',
                'pytest-pythonpath==0.7.3',
                'pytest-sugar==0.9.3',
                'pytest-watch==4.2.0',
                'PyVirtualDisplay==1.3.2',
                'webdriverwrapper==2.8.0',
                'django-simple-captcha==0.5.14',
            ],
            'build': [
                'Sphinx==1.8.5',
            ],
            'psql': [
                'psycopg2==2.8.5',
            ],
            'mysql': [
                'mysqlclient==1.3.14',
            ],
        },

        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Natural Language :: English',
            'Programming Language :: Python :: 3',
            'Topic :: Software Development :: Libraries :: Application Frameworks',
            'Framework :: Django',
            'Framework :: Django :: 2.2',
        ],
        keywords=['django', 'cms'],
    )
