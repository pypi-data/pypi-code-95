from setuptools import setup

setup(
    name='waterbear.service.cloudfront',
    version='1.0.0',
    description='Waterbear Cloud Cloudfront service',
    install_requires=['boto3','moto'],
    packages=['waterbear.service'],
    include_package_data=True,
    zip_safe=False,
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [],
    },
)

