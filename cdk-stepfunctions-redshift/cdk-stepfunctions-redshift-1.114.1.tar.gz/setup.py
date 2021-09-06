import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-stepfunctions-redshift",
    "version": "1.114.1",
    "description": "A JSII construct lib to build AWS Serverless infrastructure to orchestrate Redshift using AWS stepfunctions.",
    "license": "UNLICENSED",
    "url": "https://github.com/aws-samples/cdk-stepfunctions-redshift.git",
    "long_description_content_type": "text/markdown",
    "author": "Peter Van Bouwel<pbbouwel@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/aws-samples/cdk-stepfunctions-redshift.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_stepfunctions_redshift",
        "cdk_stepfunctions_redshift._jsii"
    ],
    "package_data": {
        "cdk_stepfunctions_redshift._jsii": [
            "cdk-stepfunctions-redshift@1.114.1.jsii.tgz"
        ],
        "cdk_stepfunctions_redshift": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-dynamodb==1.114.0",
        "aws-cdk.aws-ec2==1.114.0",
        "aws-cdk.aws-events-targets==1.114.0",
        "aws-cdk.aws-events==1.114.0",
        "aws-cdk.aws-iam==1.114.0",
        "aws-cdk.aws-kms==1.114.0",
        "aws-cdk.aws-lambda-event-sources==1.114.0",
        "aws-cdk.aws-lambda-python==1.114.0",
        "aws-cdk.aws-lambda==1.114.0",
        "aws-cdk.aws-logs==1.114.0",
        "aws-cdk.aws-redshift==1.114.0",
        "aws-cdk.aws-sam==1.114.0",
        "aws-cdk.aws-sqs==1.114.0",
        "aws-cdk.aws-stepfunctions-tasks==1.114.0",
        "aws-cdk.aws-stepfunctions==1.114.0",
        "aws-cdk.core==1.114.0",
        "aws-solutions-constructs.aws-events-rule-sqs==1.114.0",
        "aws-solutions-constructs.aws-lambda-dynamodb==1.114.0",
        "aws-solutions-constructs.aws-sqs-lambda==1.114.0",
        "constructs>=3.2.27, <4.0.0",
        "jsii>=1.34.0, <2.0.0",
        "publication>=0.0.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
