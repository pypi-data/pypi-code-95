import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-serverless-lamp",
    "version": "1.4.49",
    "description": "A JSII construct lib to build AWS Serverless LAMP with AWS CDK",
    "license": "Apache-2.0",
    "url": "https://github.com/aws-samples/cdk-serverless-lamp.git",
    "long_description_content_type": "text/markdown",
    "author": "Pahud Hsieh<hunhsieh@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/aws-samples/cdk-serverless-lamp.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_serverless_lamp",
        "cdk_serverless_lamp._jsii"
    ],
    "package_data": {
        "cdk_serverless_lamp._jsii": [
            "cdk-serverless-lamp@1.4.49.jsii.tgz"
        ],
        "cdk_serverless_lamp": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-apigateway>=1.73.0, <2.0.0",
        "aws-cdk.aws-apigatewayv2-integrations>=1.73.0, <2.0.0",
        "aws-cdk.aws-apigatewayv2>=1.73.0, <2.0.0",
        "aws-cdk.aws-ec2>=1.73.0, <2.0.0",
        "aws-cdk.aws-iam>=1.73.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.73.0, <2.0.0",
        "aws-cdk.aws-rds>=1.73.0, <2.0.0",
        "aws-cdk.aws-secretsmanager>=1.73.0, <2.0.0",
        "aws-cdk.core>=1.73.0, <2.0.0",
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
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": [
        "src/cdk_serverless_lamp/_jsii/bin/jsii-release-npm"
    ]
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
