import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "kong-control-plane",
    "version": "0.0.0",
    "description": "kong-control-plane",
    "license": "Apache-2.0",
    "url": "https://github.com/Kong/kong-aws-cdk-cp.git",
    "long_description_content_type": "text/markdown",
    "author": "Anuj Sharma<anshrma@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/Kong/kong-aws-cdk-cp.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "kong_control_plane",
        "kong_control_plane._jsii"
    ],
    "package_data": {
        "kong_control_plane._jsii": [
            "kong-control-plane@0.0.0.jsii.tgz"
        ],
        "kong_control_plane": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-acmpca>=1.122.0, <2.0.0",
        "aws-cdk.aws-autoscaling-hooktargets>=1.122.0, <2.0.0",
        "aws-cdk.aws-autoscaling>=1.122.0, <2.0.0",
        "aws-cdk.aws-certificatemanager>=1.122.0, <2.0.0",
        "aws-cdk.aws-ec2>=1.122.0, <2.0.0",
        "aws-cdk.aws-eks>=1.122.0, <2.0.0",
        "aws-cdk.aws-elasticache>=1.122.0, <2.0.0",
        "aws-cdk.aws-elasticsearch>=1.122.0, <2.0.0",
        "aws-cdk.aws-events-targets>=1.122.0, <2.0.0",
        "aws-cdk.aws-events>=1.122.0, <2.0.0",
        "aws-cdk.aws-iam>=1.122.0, <2.0.0",
        "aws-cdk.aws-kms>=1.122.0, <2.0.0",
        "aws-cdk.aws-logs>=1.122.0, <2.0.0",
        "aws-cdk.aws-rds>=1.122.0, <2.0.0",
        "aws-cdk.aws-route53>=1.122.0, <2.0.0",
        "aws-cdk.aws-secretsmanager>=1.122.0, <2.0.0",
        "aws-cdk.aws-sqs>=1.122.0, <2.0.0",
        "aws-cdk.core>=1.122.0, <2.0.0",
        "constructs>=3.2.27, <4.0.0",
        "jsii>=1.34.0, <2.0.0",
        "kong-core<0.0.1",
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
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
