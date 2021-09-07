from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

with open('VERSION') as file:
    VERSION = file.read()
    VERSION = ''.join(VERSION.split())

setup(
    name='b-cfn-s3-large-deployment',
    version=VERSION,
    license='Apache License 2.0',
    packages=find_packages(exclude=[
        # Exclude virtual environment.
        'venv',
        # Exclude test source files.
        'b_cfn_s3_large_deployment_tests'
    ]),
    description=(
        'AWS CDK custom resource that handles large files deployment to S3 bucket.'
    ),
    long_description=README + '\n\n' + HISTORY,
    long_description_content_type='text/markdown',
    include_package_data=True,
    install_requires=[
        'aws-cdk.aws-ec2>=1.120.0,<2.0.0',
        'aws-cdk.aws-iam>=1.120.0,<2.0.0',
        'aws-cdk.aws-lambda>=1.120.0,<2.0.0',
        'aws-cdk.aws-s3>=1.120.0,<2.0.0',
        'aws-cdk.aws-s3-assets>=1.120.0,<2.0.0',
        'aws-cdk.core>=1.120.0,<2.0.0',
        'aws-cdk.lambda-layer-awscli>=1.120.0,<2.0.0',

        'boto3>=1.18.32<2.0.0',
        'urllib3>=1.26.6,<2.0.0',
    ],
    author='Matas Gumbinas',
    author_email='matas.gumbinas@biomapas.com',
    keywords='AWS CDK Lambda Layer S3 Deployment',
    url='https://github.com/Biomapas/B.CfnS3LargeDeployment',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
