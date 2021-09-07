from distutils.core import setup
import setuptools

setup(
    name='matialvarezs_handlers_easy',
    packages=['matialvarezs_handlers_easy'],  # this must be the same as the name above
    version='0.1.58',
    install_requires=[
        'django-json-response==1.1.3',
        'celery>=4.1.0,<5',
        'django-celery-results==1.0.1',
        'arrow==0.13.1',
        'python-dateutil==2.8.1',
        'pytz',
        'python-crontab',
        'paho-mqtt==1.5.0'
    ],
    include_package_data=True,
    description='Easy handler',
    author='Matias Alvarez Sabate',
    author_email='matialvarezs@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3.5',
    ],
)


# from distutils.core import setup
# import setuptools
#
# setuptools.setup(
#     name='matialvarezs_handlers_easy',
#     packages=setuptools.find_packages(),  # this must be the same as the name above
#     version='0.1.40',
#     install_requires=[
#         'django-json-response==1.1.3',
#         'celery==4.1.0',
#         'django-celery-results==1.0.1',
#         'arrow==0.13.1',
#         'python-dateutil==2.8.0',
#         'pytz',
#         'python-crontab'
#     ],
#     include_package_data=True,
#     description='Easy handler',
#     author='Matias Alvarez Sabate',
#     author_email='matialvarezs@gmail.com',
#     classifiers=[
#         'Programming Language :: Python :: 3.5',
#     ],
# )
